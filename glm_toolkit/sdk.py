#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLM-5.1 API SDK
Core client for interacting with GLM-5.1 API
"""

import os
import time
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    import ujson as json
except ImportError:
    import json


@dataclass
class GLMMessage:
    """Message format for GLM-5.1 API"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary format"""
        return {
            "role": self.role,
            "content": self.content
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GLMMessage':
        """Create message from dictionary"""
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None
        )


@dataclass
class GLMResponse:
    """Response from GLM-5.1 API"""
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    request_id: Optional[str] = None
    created_at: Optional[datetime] = None
    raw_response: Optional[Dict] = None

    def __str__(self) -> str:
        """String representation of response"""
        return self.content

    @property
    def total_tokens(self) -> int:
        """Get total tokens used"""
        return self.usage.get("total_tokens", 0)

    @property
    def prompt_tokens(self) -> int:
        """Get prompt tokens used"""
        return self.usage.get("prompt_tokens", 0)

    @property
    def completion_tokens(self) -> int:
        """Get completion tokens used"""
        return self.usage.get("completion_tokens", 0)


class GLMAPIClient:
    """
    GLM-5.1 API Client with advanced features

    Features:
    - Automatic retry with exponential backoff
    - Request caching support
    - Token usage tracking
    - Batch processing
    - Custom model selection
    """

    DEFAULT_API_URL = "https://open.bigmodel.cn/api/paas/v4"
    DEFAULT_MODEL = "glm-5.1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        cache_manager=None,
        rate_limiter=None,
        **kwargs
    ):
        """
        Initialize GLM-5.1 API Client

        Args:
            api_key: API key for authentication (defaults to ENV variable)
            api_url: Custom API endpoint URL
            model: Model name to use (default: glm-5.1)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            cache_manager: Optional cache manager instance
            rate_limiter: Optional rate limiter instance
        """
        self.api_key = api_key or os.environ.get("GLM_API_KEY", "")
        if not self.api_key:
            raise ValueError("API key is required. Set GLM_API_KEY environment variable or pass api_key parameter.")

        self.api_url = api_url or os.environ.get("GLM_API_URL", self.DEFAULT_API_URL)
        self.model = model or self.DEFAULT_MODEL
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_manager = cache_manager
        self.rate_limiter = rate_limiter

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "GLM-5.1-Toolkit/1.0.0"
        })

    def _make_request(
        self,
        messages: List[Union[Dict[str, str], GLMMessage]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make API request with retry logic

        Args:
            messages: List of message dictionaries or GLMMessage objects
            **kwargs: Additional parameters for API

        Returns:
            API response as dictionary
        """
        if self.rate_limiter:
            self.rate_limiter.wait()

        # Convert GLMMessage objects to dictionaries
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, GLMMessage):
                formatted_messages.append(msg.to_dict())
            else:
                formatted_messages.append(msg)

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": formatted_messages,
            **kwargs
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        cache_key = self._generate_cache_key(payload)
        if self.cache_manager:
            cached_response = self.cache_manager.get(cache_key)
            if cached_response:
                return cached_response

        @retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=10)
        )
        def _request():
            response = self.session.post(
                f"{self.api_url}/chat/completions",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 429:
                raise Exception("Rate limit exceeded")

            response.raise_for_status()
            return response.json()

        result = _request()

        if self.cache_manager:
            self.cache_manager.set(cache_key, result)

        return result

    def _generate_cache_key(self, payload: Dict) -> str:
        """Generate cache key from request payload"""
        import hashlib
        content = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def chat(
        self,
        messages: List[Union[Dict[str, str], GLMMessage]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        stream: bool = False,
        **kwargs
    ) -> GLMResponse:
        """
        Send chat completion request

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 - 2.0)
            max_tokens: Maximum tokens in response
            top_p: Nucleus sampling parameter
            stream: Enable streaming response
            **kwargs: Additional parameters

        Returns:
            GLMResponse object
        """
        response_data = self._make_request(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=stream,
            **kwargs
        )

        return GLMResponse(
            content=response_data["choices"][0]["message"]["content"],
            model=response_data.get("model", self.model),
            usage=response_data.get("usage", {}),
            request_id=response_data.get("id"),
            created_at=datetime.fromisoformat(response_data["created"]) if "created" in response_data else None,
            raw_response=response_data
        )

    def simple_chat(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple chat interface with single prompt

        Args:
            prompt: User message
            system_message: Optional system message
            **kwargs: Additional parameters

        Returns:
            Response content as string
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = self.chat(messages, **kwargs)
        return response.content

    def batch_chat(
        self,
        prompts: List[str],
        system_message: Optional[str] = None,
        show_progress: bool = True,
        **kwargs
    ) -> List[str]:
        """
        Process multiple prompts in batch

        Args:
            prompts: List of user prompts
            system_message: Optional system message
            show_progress: Show progress bar
            **kwargs: Additional parameters

        Returns:
            List of response strings
        """
        from rich.progress import Progress, SpinnerColumn, TextColumn

        results = []

        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Processing {len(prompts)} prompts...",
                    total=len(prompts)
                )

                for prompt in prompts:
                    result = self.simple_chat(prompt, system_message, **kwargs)
                    results.append(result)
                    progress.update(task, advance=1)
        else:
            for prompt in prompts:
                result = self.simple_chat(prompt, system_message, **kwargs)
                results.append(result)

        return results

    def chat_stream(
        self,
        messages: List[Union[Dict[str, str], GLMMessage]],
        **kwargs
    ):
        """
        Stream chat completion response

        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters

        Yields:
            Content chunks as they arrive
        """
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [msg.to_dict() if isinstance(msg, GLMMessage) else msg for msg in messages],
            "stream": True,
            **{k: v for k, v in kwargs.items() if k != "model" and v is not None}
        }

        if self.rate_limiter:
            self.rate_limiter.wait()

        response = self.session.post(
            f"{self.api_url}/chat/completions",
            json=payload,
            timeout=self.timeout,
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    chunk = json.loads(data)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        if 'content' in delta:
                            yield delta['content']

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics

        Returns:
            Dictionary with usage information
        """
        return {
            "model": self.model,
            "api_url": self.api_url,
            "cache_enabled": self.cache_manager is not None,
            "rate_limit_enabled": self.rate_limiter is not None
        }

    def close(self):
        """Close the client session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
