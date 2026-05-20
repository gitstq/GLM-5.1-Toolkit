#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for GLM-5.1 API Toolkit
"""

import pytest
import os
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Set test environment
os.environ['GLM_API_KEY'] = 'test_api_key_12345'


class TestGLMMessage:
    """Tests for GLMMessage dataclass"""

    def test_message_creation(self):
        """Test creating a message"""
        from glm_toolkit.sdk import GLMMessage

        msg = GLMMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_to_dict(self):
        """Test converting message to dictionary"""
        from glm_toolkit.sdk import GLMMessage

        msg = GLMMessage(role="assistant", content="Hi there")
        data = msg.to_dict()

        assert data["role"] == "assistant"
        assert data["content"] == "Hi there"

    def test_message_from_dict(self):
        """Test creating message from dictionary"""
        from glm_toolkit.sdk import GLMMessage

        data = {"role": "system", "content": "You are helpful"}
        msg = GLMMessage.from_dict(data)

        assert msg.role == "system"
        assert msg.content == "You are helpful"


class TestGLMResponse:
    """Tests for GLMResponse dataclass"""

    def test_response_creation(self):
        """Test creating a response"""
        from glm_toolkit.sdk import GLMResponse

        resp = GLMResponse(
            content="Test response",
            model="glm-5.1",
            usage={"total_tokens": 100}
        )

        assert resp.content == "Test response"
        assert resp.model == "glm-5.1"
        assert resp.total_tokens == 100

    def test_response_string(self):
        """Test response string representation"""
        from glm_toolkit.sdk import GLMResponse

        resp = GLMResponse(content="Hello", model="glm-5.1")
        assert str(resp) == "Hello"

    def test_response_token_properties(self):
        """Test response token properties"""
        from glm_toolkit.sdk import GLMResponse

        resp = GLMResponse(
            content="Test",
            model="glm-5.1",
            usage={
                "prompt_tokens": 50,
                "completion_tokens": 30,
                "total_tokens": 80
            }
        )

        assert resp.prompt_tokens == 50
        assert resp.completion_tokens == 30
        assert resp.total_tokens == 80


class TestConfig:
    """Tests for configuration management"""

    def test_config_default_values(self):
        """Test default configuration values"""
        from glm_toolkit.config import Config

        config = Config()
        assert config.model == "glm-5.1"
        assert config.timeout == 120
        assert config.max_retries == 3

    def test_config_from_dict(self):
        """Test creating config from dictionary"""
        from glm_toolkit.config import Config

        data = {
            "model": "glm-4",
            "timeout": 60,
            "custom_field": "value"
        }

        config = Config.from_dict(data)
        assert config.model == "glm-4"
        assert config.timeout == 60

    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        from glm_toolkit.config import Config

        config = Config(model="glm-5", timeout=90)
        data = config.to_dict()

        assert data["model"] == "glm-5"
        assert data["timeout"] == 90


class TestCacheManager:
    """Tests for cache management"""

    def test_cache_initialization(self, tmp_path):
        """Test cache initialization"""
        try:
            from glm_toolkit.cache import CacheManager

            cache_dir = tmp_path / "cache"
            cache = CacheManager(cache_dir=str(cache_dir), max_size=1024*1024)

            assert cache_dir.exists()
            cache.close()
        except ImportError:
            pytest.skip("diskcache not installed")

    def test_cache_set_get(self, tmp_path):
        """Test cache set and get operations"""
        try:
            from glm_toolkit.cache import CacheManager

            cache_dir = tmp_path / "cache"
            cache = CacheManager(cache_dir=str(cache_dir))

            cache.set("test_key", {"data": "test_value"})
            result = cache.get("test_key")

            assert result is not None
            assert result["data"] == "test_value"

            cache.close()
        except ImportError:
            pytest.skip("diskcache not installed")

    def test_cache_stats(self, tmp_path):
        """Test cache statistics"""
        try:
            from glm_toolkit.cache import CacheManager

            cache_dir = tmp_path / "cache"
            cache = CacheManager(cache_dir=str(cache_dir))

            cache.set("key1", "value1")
            cache.get("key1")
            cache.get("nonexistent")

            stats = cache.get_stats()

            assert "hits" in stats
            assert "misses" in stats
            assert stats["hits"] == 1
            assert stats["misses"] == 1

            cache.close()
        except ImportError:
            pytest.skip("diskcache not installed")


class TestRateLimiter:
    """Tests for rate limiting"""

    def test_rate_limiter_init(self):
        """Test rate limiter initialization"""
        from glm_toolkit.rate_limiter import RateLimiter

        limiter = RateLimiter(requests=10, period=1.0, burst=5)

        assert limiter.config.requests == 10
        assert limiter.config.period == 1.0
        assert limiter.config.burst == 5

    def test_rate_limiter_wait(self):
        """Test rate limiter wait method"""
        from glm_toolkit.rate_limiter import RateLimiter

        limiter = RateLimiter(requests=100, period=1.0, burst=10)

        # Should not block on first call
        start = time.time()
        limiter.wait()
        elapsed = time.time() - start

        assert elapsed < 0.1

    def test_rate_limiter_try_acquire(self):
        """Test rate limiter try_acquire method"""
        from glm_toolkit.rate_limiter import RateLimiter

        limiter = RateLimiter(requests=2, period=1.0, burst=2)

        assert limiter.try_acquire() is True
        assert limiter.try_acquire() is True
        assert limiter.try_acquire() is False

    def test_rate_limiter_stats(self):
        """Test rate limiter statistics"""
        from glm_toolkit.rate_limiter import RateLimiter

        limiter = RateLimiter(requests=10, period=1.0, burst=5)

        limiter.wait()
        limiter.try_acquire()

        stats = limiter.get_stats()

        assert stats["total_requests"] == 2
        assert "config" in stats


class TestBatchProcessor:
    """Tests for batch processing"""

    def test_load_json_input(self, tmp_path):
        """Test loading JSON input file"""
        from glm_toolkit.batch import BatchProcessor

        input_file = tmp_path / "input.json"
        with open(input_file, 'w') as f:
            json.dump([
                {"prompt": "Hello 1"},
                {"prompt": "Hello 2"}
            ], f)

        mock_client = Mock()
        processor = BatchProcessor(mock_client)

        items = processor._load_input_file(input_file)

        assert len(items) == 2
        assert items[0]["prompt"] == "Hello 1"

    def test_load_txt_input(self, tmp_path):
        """Test loading TXT input file"""
        from glm_toolkit.batch import BatchProcessor

        input_file = tmp_path / "input.txt"
        with open(input_file, 'w') as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        mock_client = Mock()
        processor = BatchProcessor(mock_client)

        items = processor._load_input_file(input_file)

        assert len(items) == 3
        assert items[0]["prompt"] == "Line 1"


class TestCLI:
    """Tests for CLI commands"""

    def test_cli_help(self):
        """Test CLI help output"""
        from glm_toolkit.cli import main
        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(main, ['--help'])

        assert result.exit_code == 0
        assert 'GLM-5.1' in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
