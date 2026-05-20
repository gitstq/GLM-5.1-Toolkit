#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limiter for GLM-5.1 API Requests
"""

import time
import threading
from typing import Dict, Optional
from collections import deque
from dataclasses import dataclass, field


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests: int = 60  # Number of requests
    period: float = 60.0  # Time period in seconds
    burst: int = 10  # Burst allowance

    def __post_init__(self):
        """Validate configuration"""
        if self.requests <= 0:
            raise ValueError("requests must be positive")
        if self.period <= 0:
            raise ValueError("period must be positive")


class RateLimiter:
    """
    Token bucket rate limiter for API requests

    Features:
    - Token bucket algorithm
    - Thread-safe operations
    - Configurable limits
    - Automatic waiting
    """

    def __init__(
        self,
        requests: int = 60,
        period: float = 60.0,
        burst: Optional[int] = None
    ):
        """
        Initialize rate limiter

        Args:
            requests: Maximum requests per period
            period: Time period in seconds
            burst: Maximum burst allowance (defaults to requests)
        """
        self.config = RateLimitConfig(
            requests=requests,
            period=period,
            burst=burst or requests
        )

        self.tokens = self.config.burst
        self.last_update = time.time()
        self.lock = threading.Lock()

        self.stats = {
            "total_requests": 0,
            "total_waits": 0,
            "total_wait_time": 0.0
        }

    def _refill_tokens(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_update

        # Calculate tokens to add
        tokens_to_add = elapsed * (self.config.requests / self.config.period)

        # Update tokens (capped at burst limit)
        self.tokens = min(self.config.burst, self.tokens + tokens_to_add)
        self.last_update = now

    def wait(self):
        """
        Wait until a request can be made

        This method blocks until a request can be processed.
        """
        with self.lock:
            self._refill_tokens()

            if self.tokens < 1:
                # Calculate wait time for one token
                wait_time = (1 - self.tokens) * (self.config.period / self.config.requests)

                self.stats["total_waits"] += 1
                self.stats["total_wait_time"] += wait_time

                time.sleep(wait_time)
                self._refill_tokens()

            # Consume one token
            self.tokens -= 1
            self.stats["total_requests"] += 1

    def try_acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Try to acquire a token without blocking

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if token acquired, False otherwise
        """
        start_time = time.time()

        while True:
            with self.lock:
                self._refill_tokens()

                if self.tokens >= 1:
                    self.tokens -= 1
                    self.stats["total_requests"] += 1
                    return True

            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return False

            # Sleep briefly before retrying
            time.sleep(0.01)

    def get_stats(self) -> Dict:
        """
        Get rate limiter statistics

        Returns:
            Dictionary with statistics
        """
        with self.lock:
            return {
                **self.stats,
                "current_tokens": self.tokens,
                "config": {
                    "requests": self.config.requests,
                    "period": self.config.period,
                    "burst": self.config.burst
                },
                "avg_wait_time": (
                    self.stats["total_wait_time"] / self.stats["total_waits"]
                    if self.stats["total_waits"] > 0 else 0
                )
            }

    def reset(self):
        """Reset rate limiter state"""
        with self.lock:
            self.tokens = self.config.burst
            self.last_update = time.time()


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter implementation

    More accurate than token bucket for smooth rate limiting.
    """

    def __init__(
        self,
        requests: int = 60,
        period: float = 60.0
    ):
        """
        Initialize sliding window rate limiter

        Args:
            requests: Maximum requests per period
            period: Time period in seconds
        """
        self.max_requests = requests
        self.window_size = period
        self.requests_log = deque()
        self.lock = threading.Lock()

    def _cleanup_old_requests(self):
        """Remove requests outside the current window"""
        current_time = time.time()
        cutoff_time = current_time - self.window_size

        while self.requests_log and self.requests_log[0] < cutoff_time:
            self.requests_log.popleft()

    def wait(self):
        """
        Wait until a request can be made
        """
        with self.lock:
            self._cleanup_old_requests()

            while len(self.requests_log) >= self.max_requests:
                # Wait until the oldest request expires
                oldest = self.requests_log[0]
                wait_time = oldest + self.window_size - time.time()

                if wait_time > 0:
                    time.sleep(wait_time)
                    self._cleanup_old_requests()

            self.requests_log.append(time.time())

    def get_stats(self) -> Dict:
        """
        Get rate limiter statistics
        """
        with self.lock:
            self._cleanup_old_requests()
            return {
                "current_requests": len(self.requests_log),
                "max_requests": self.max_requests,
                "window_size": self.window_size,
                "available_slots": self.max_requests - len(self.requests_log)
            }
