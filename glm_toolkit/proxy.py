#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Proxy Server for GLM-5.1
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import threading
import hashlib

try:
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS
except ImportError:
    Flask = None

from .config import ConfigManager
from .cache import CacheManager
from .rate_limiter import RateLimiter, SlidingWindowRateLimiter

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    """Proxy server configuration"""
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    cache_enabled: bool = True
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 60
    rate_limit_period: float = 60.0
    max_request_size: int = 10 * 1024 * 1024  # 10MB


class ProxyState:
    """State management for proxy server"""

    def __init__(self, config: ProxyConfig):
        self.config = config
        self.client = None
        self.cache = None
        self.rate_limiter = None
        self.request_count = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

        self._initialize_components()

    def _initialize_components(self):
        """Initialize proxy components"""
        # Load config
        config_manager = ConfigManager()
        api_config = config_manager.get_config()

        # Initialize API client
        from .sdk import GLMAPIClient
        self.client = GLMAPIClient(
            api_key=api_config.api_key,
            api_url=api_config.api_url,
            model=api_config.model,
            timeout=api_config.timeout
        )

        # Initialize cache
        if self.config.cache_enabled:
            try:
                self.cache = CacheManager(cache_dir=api_config.cache_dir)
            except Exception as e:
                logger.warning(f"Cache initialization failed: {e}")

        # Initialize rate limiter
        if self.config.rate_limit_enabled:
            self.rate_limiter = SlidingWindowRateLimiter(
                requests=self.config.rate_limit_requests,
                period=self.config.rate_limit_period
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        return {
            "uptime": time.time() - self.start_time,
            "request_count": self.request_count,
            "requests_per_second": self.request_count / (time.time() - self.start_time),
            "cache_enabled": self.cache is not None,
            "rate_limit_enabled": self.rate_limiter is not None,
            "config": {
                "host": self.config.host,
                "port": self.config.port,
                "debug": self.config.debug
            }
        }


# Global state
proxy_state = None


@app.before_request
def before_request():
    """Pre-request processing"""
    global proxy_state

    # Rate limiting
    if proxy_state and proxy_state.rate_limiter:
        proxy_state.rate_limiter.wait()

    # Update request count
    if proxy_state:
        with proxy_state.lock:
            proxy_state.request_count += 1


@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """
    Proxy endpoint for chat completions

    Compatible with OpenAI API format
    """
    global proxy_state

    if not proxy_state or not proxy_state.client:
        return jsonify({"error": "Proxy not initialized"}), 500

    try:
        # Validate content length
        if request.content_length and request.content_length > proxy_state.config.max_request_size:
            return jsonify({"error": "Request too large"}), 413

        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        messages = data.get('messages', [])
        model = data.get('model', proxy_state.client.model)
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens')

        # Generate cache key
        cache_key = _generate_cache_key(data)

        # Check cache
        if proxy_state.cache:
            cached_response = proxy_state.cache.get(cache_key)
            if cached_response:
                logger.info(f"Cache hit for key: {cache_key[:16]}...")
                cached_response["cached"] = True
                return jsonify(cached_response)

        # Make API request
        response = proxy_state.client.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Build response
        response_data = {
            "id": response.request_id or f"glm-{int(time.time())}",
            "object": "chat.completion",
            "created": int(response.created_at.timestamp()) if response.created_at else int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response.content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "total_tokens": response.total_tokens
            },
            "cached": False
        }

        # Cache response
        if proxy_state.cache:
            proxy_state.cache.set(cache_key, response_data)

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Request error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/v1/models', methods=['GET'])
def list_models():
    """List available models"""
    return jsonify({
        "object": "list",
        "data": [{
            "id": "glm-5.1",
            "object": "model",
            "created": 20240101,
            "owned_by": "Zhipu AI",
            "permission": [],
            "root": "glm-5.1",
            "parent": None
        }]
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time()
    })


@app.route('/stats', methods=['GET'])
def stats():
    """Get proxy statistics"""
    global proxy_state
    if proxy_state:
        return jsonify(proxy_state.get_stats())
    return jsonify({"error": "Proxy not initialized"}), 500


def _generate_cache_key(data: Dict) -> str:
    """Generate cache key from request data"""
    content = json.dumps(data, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


def create_app(config: Optional[ProxyConfig] = None) -> Flask:
    """
    Create Flask application with configuration

    Args:
        config: Optional proxy configuration

    Returns:
        Configured Flask application
    """
    global proxy_state

    if config is None:
        config = ProxyConfig()

    proxy_state = ProxyState(config)

    return app


def main():
    """Main entry point for proxy server"""
    import argparse

    parser = argparse.ArgumentParser(description='GLM-5.1 API Proxy Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--no-rate-limit', action='store_true', help='Disable rate limiting')
    parser.add_argument('--rate-limit', type=int, default=60, help='Rate limit (requests per period)')
    parser.add_argument('--rate-period', type=float, default=60.0, help='Rate limit period in seconds')

    args = parser.parse_args()

    config = ProxyConfig(
        host=args.host,
        port=args.port,
        debug=args.debug,
        cache_enabled=not args.no_cache,
        rate_limit_enabled=not args.no_rate_limit,
        rate_limit_requests=args.rate_limit,
        rate_limit_period=args.rate_period
    )

    proxy = create_app(config)

    logger.info(f"Starting GLM-5.1 Proxy on {config.host}:{config.port}")
    proxy.run(
        host=config.host,
        port=config.port,
        debug=config.debug
    )


if __name__ == '__main__':
    main()
