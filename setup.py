#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLM-5.1 API Toolkit & Proxy
Author: GitHub/gitstq
License: MIT
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="glm-api-toolkit",
    version="1.0.0",
    author="GitHub/gitstq",
    author_email="gitstq@example.com",
    description="GLM-5.1 API Toolkit & Proxy - Comprehensive API management tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/GLM-5.1-Toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "click>=8.0.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "diskcache>=5.4.0",
        "tenacity>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "glm-toolkit=glm_toolkit.cli:main",
            "glm-proxy=glm_toolkit.proxy:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
