#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Management for GLM-5.1 API Toolkit
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration container"""
    api_key: str = ""
    api_url: str = "https://open.bigmodel.cn/api/paas/v4"
    model: str = "glm-5.1"
    timeout: int = 120
    max_retries: int = 3
    cache_enabled: bool = True
    cache_dir: str = "~/.glm_toolkit/cache"
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 60
    rate_limit_period: int = 60
    log_level: str = "INFO"
    extra_params: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create Config from dictionary"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})

    def to_dict(self) -> Dict[str, Any]:
        """Convert Config to dictionary"""
        return {
            "api_key": self.api_key,
            "api_url": self.api_url,
            "model": self.model,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "cache_enabled": self.cache_enabled,
            "cache_dir": self.cache_dir,
            "rate_limit_enabled": self.rate_limit_enabled,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_period": self.rate_limit_period,
            "log_level": self.log_level,
            "extra_params": self.extra_params
        }


class ConfigManager:
    """
    Manage configuration with multiple sources:
    - Environment variables
    - Configuration file (~/.glm_toolkit/config.yaml)
    - Default values
    """

    DEFAULT_CONFIG_DIR = Path.home() / ".glm_toolkit"
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager

        Args:
            config_file: Custom configuration file path
        """
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.config = self._load_config()

    def _load_config(self) -> Config:
        """Load configuration from all sources"""
        # Start with default values
        config = Config()

        # Load from config file
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    for key, value in file_config.items():
                        if hasattr(config, key):
                            setattr(config, key, value)

        # Override with environment variables
        if os.getenv("GLM_API_KEY"):
            config.api_key = os.getenv("GLM_API_KEY")
        if os.getenv("GLM_API_URL"):
            config.api_url = os.getenv("GLM_API_URL")
        if os.getenv("GLM_MODEL"):
            config.model = os.getenv("GLM_MODEL")
        if os.getenv("GLM_TIMEOUT"):
            config.timeout = int(os.getenv("GLM_TIMEOUT"))
        if os.getenv("GLM_LOG_LEVEL"):
            config.log_level = os.getenv("GLM_LOG_LEVEL")

        return config

    def save_config(self, config: Optional[Config] = None):
        """
        Save configuration to file

        Args:
            config: Configuration to save (uses current config if None)
        """
        if config is None:
            config = self.config

        self.DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, 'w') as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False)

    def get_config(self) -> Config:
        """Get current configuration"""
        return self.config

    def update_config(self, **kwargs):
        """
        Update configuration values

        Args:
            **kwargs: Configuration values to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    @classmethod
    def init_config(cls, api_key: str, **kwargs) -> 'ConfigManager':
        """
        Initialize configuration with API key

        Args:
            api_key: GLM API key
            **kwargs: Additional configuration

        Returns:
            ConfigManager instance
        """
        manager = cls()
        manager.update_config(api_key=api_key, **kwargs)
        manager.save_config()
        return manager
