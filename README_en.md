# 🌟 GLM-5.1 API Toolkit & Proxy

[简体中文](./README_zh-CN.md) | [繁體中文](./README_zh-TW.md) | [English](./README_en.md) | [日本語](./README_ja.md)

---

## 🎉 Project Introduction

**GLM-5.1 API Toolkit & Proxy** is a comprehensive API management toolkit designed specifically for the GLM-5.1 model, providing three core functionalities: Python SDK, CLI tools, and API Proxy server.

### ✨ Core Values

🛡️ **Privacy First** - Local caching keeps sensitive data secure

⚡ **High Performance** - Smart caching + rate limiting for efficient API quota utilization

🔧 **Complete Features** - SDK / CLI / Proxy integrated to meet all usage scenarios

🌐 **Multi-language Docs** - Full coverage in Simplified/Traditional Chinese, English, Japanese

### 🎯 Complementary Relationship with GLM-Researcher

| Project | Focus | Core Features |
|---------|-------|---------------|
| **GLM-Researcher** | Academic Writing Assistant | Focus on academic paper research and writing |
| **GLM-5.1-Toolkit** | API Management Toolkit | API calls, batch processing, proxy services |

## ✨ Core Features

- 🐍 **Python SDK** - Clean and easy-to-use Python interface with streaming, batch processing, auto-retry
- 💻 **CLI Tools** - Complete chat, batch processing, config management with single commands
- 🌐 **API Proxy** - Proxy server with caching and rate limiting, OpenAI API compatible
- 💾 **Smart Caching** - Automatic API response caching to save quota and speed up access
- ⚡ **Rate Limiting** - Intelligent flow control algorithm to protect API quota
- 🔄 **Auto Retry** - Automatic retry on network fluctuations, stable and reliable
- 📊 **Statistics Monitoring** - Real-time usage statistics and cache hit rates
- 🧩 **Modular Design** - Flexible combinations, use what you need

## 🚀 Quick Start

### 📦 Installation

```bash
# Install with pip
pip install glm-api-toolkit

# Or install from source
git clone https://github.com/gitstq/GLM-5.1-Toolkit.git
cd GLM-5.1-Toolkit
pip install -e .
```

### ⚙️ Configure API Key

```bash
# Set environment variable
export GLM_API_KEY=your_api_key_here

# Or use CLI to configure
glm-toolkit config --set-api-key your_api_key_here
```

### 💬 Quick Chat

```bash
glm-toolkit chat "Hello, please introduce the GLM-5.1 model"
```

### 🌐 Start Proxy Server

```bash
glm-proxy --port 8080
```

### 📝 Python SDK Usage

```python
from glm_toolkit import GLMAPIClient

# Initialize client
client = GLMAPIClient(api_key="your_api_key")

# Simple chat
response = client.simple_chat("Hello, GLM!")
print(response)

# Chat with context
messages = [
    {"role": "system", "content": "You are a professional Python programmer"},
    {"role": "user", "content": "How to implement quicksort?"}
]
response = client.chat(messages)
print(response.content)
```

## 📖 Detailed Usage Guide

### 🔧 CLI Commands

#### Interactive Chat
```bash
glm-toolkit chat "Your question" --temperature 0.7 --max-tokens 500
```

#### Batch Processing
```bash
# Prepare input file (input.json)
# [
#   {"prompt": "Question 1"},
#   {"prompt": "Question 2"}
# ]

glm-toolkit batch -i input.json -o output.json --workers 5
```

#### Configuration Management
```bash
# Show current configuration
glm-toolkit config --show

# Update configuration
glm-toolkit config --set-model glm-5.1
glm-toolkit config --set-api-url https://custom.api.url
```

#### Cache Management
```bash
# Show cache statistics
glm-toolkit cache

# Clear cache
glm-toolkit cache --clear
```

### 🐍 Python SDK Advanced Usage

#### Streaming Response
```python
for chunk in client.chat_stream(messages):
    print(chunk, end='', flush=True)
```

#### Batch Processing
```python
results = client.batch_chat([
    "Question 1",
    "Question 2",
    "Question 3"
], show_progress=True)
```

#### Custom Caching
```python
from glm_toolkit import CacheManager, RateLimiter

cache = CacheManager(ttl=3600)  # 1 hour cache
limiter = RateLimiter(requests=60, period=60)  # 60 requests per minute

client = GLMAPIClient(
    api_key="your_key",
    cache_manager=cache,
    rate_limiter=limiter
)
```

### 🌐 API Proxy Usage

The proxy service is compatible with OpenAI API format, can directly replace existing API endpoints:

```bash
# Start proxy
glm-proxy --port 8080 --rate-limit 60

# OpenAI format call
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5.1",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 💡 Design Philosophy & Roadmap

### 🎨 Design Principles

1. **Modular Architecture** - Independent core SDK, CLI and Proxy built on SDK
2. **Configuration First** - Config file + Environment variables + CLI arguments
3. **Fault Tolerance** - Auto retry, rate limiting protection, graceful degradation
4. **Performance First** - Async processing, connection reuse, smart caching

### 📋 Roadmap

- [ ] v1.1 - Add WebSocket streaming support
- [ ] v1.2 - Multi-API Key load balancing
- [ ] v1.3 - Support GLM-4-All model
- [ ] v2.0 - Web management interface
- [ ] v2.1 - Docker one-click deployment

## 📦 Packaging & Deployment

### 🐳 Docker Deployment

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["glm-proxy", "--host", "0.0.0.0", "--port", "8080"]
```

### ☁️ Cloud Function Deployment

```python
# handler.py
from glm_toolkit import GLMAPIClient

def handle(event, context):
    client = GLMAPIClient(api_key=os.environ['GLM_API_KEY'])
    data = json.loads(event.body)
    response = client.chat(data['messages'])
    return {'statusCode': 200, 'body': json.dumps(response.content)}
```

## 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

⭐ If this project is helpful to you, please star it!

📧 Questions? Feel free to submit an [Issue](https://github.com/gitstq/GLM-5.1-Toolkit/issues)
