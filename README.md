# 🌟 GLM-5.1 API Toolkit & Proxy

[简体中文](./README_zh-CN.md) | [繁體中文](./README_zh-TW.md) | [English](./README_en.md) | [日本語](./README_ja.md)

---

## 🎉 项目介绍

**GLM-5.1 API Toolkit & Proxy** 是一款专为 GLM-5.1 模型打造的综合 API 管理工具包，提供 Python SDK、命令行工具和 API 代理服务器三大核心功能。

### ✨ 核心价值

🛡️ **隐私优先** - 本地缓存，敏感数据不外泄

⚡ **性能卓越** - 智能缓存 + 速率限制，高效利用 API 配额

🔧 **功能完整** - SDK / CLI / Proxy 三位一体，满足所有使用场景

🌐 **多语言文档** - 简体中文、繁体中文、English、日本語全方位覆盖

### 🎯 与 GLM-Researcher 的互补关系

| 项目 | 定位 | 核心功能 |
|------|------|----------|
| **GLM-Researcher** | 学术写作助手 | 专注于学术论文研究与写作 |
| **GLM-5.1-Toolkit** | API 管理工具包 | API 调用、批处理、代理服务 |

## ✨ 核心特性

- 🐍 **Python SDK** - 简洁易用的 Python 接口，支持流式响应、批处理、自动重试
- 💻 **CLI 工具** - 一行命令完成聊天、批处理、配置管理
- 🌐 **API 代理** - 支持缓存、速率限制的代理服务器，兼容 OpenAI API 格式
- 💾 **智能缓存** - 自动缓存 API 响应，节省配额加速访问
- ⚡ **速率限制** - 智能限流算法，保护 API 配额
- 🔄 **自动重试** - 网络波动自动重试，稳定可靠
- 📊 **统计监控** - 实时查看使用情况与缓存命中率
- 🧩 **模块化设计** - 灵活组合，按需使用

## 🚀 快速开始

### 📦 安装

```bash
# 使用 pip 安装
pip install glm-api-toolkit

# 或从源码安装
git clone https://github.com/gitstq/GLM-5.1-Toolkit.git
cd GLM-5.1-Toolkit
pip install -e .
```

### ⚙️ 配置 API Key

```bash
# 设置环境变量
export GLM_API_KEY=your_api_key_here

# 或使用 CLI 配置
glm-toolkit config --set-api-key your_api_key_here
```

### 💬 快速聊天

```bash
glm-toolkit chat "你好，请介绍一下GLM-5.1模型"
```

### 🌐 启动代理服务

```bash
glm-proxy --port 8080
```

### 📝 Python SDK 使用

```python
from glm_toolkit import GLMAPIClient

# 初始化客户端
client = GLMAPIClient(api_key="your_api_key")

# 简单聊天
response = client.simple_chat("你好，GLM！")
print(response)

# 带上下文的聊天
messages = [
    {"role": "system", "content": "你是一个专业的Python程序员"},
    {"role": "user", "content": "如何实现快速排序？"}
]
response = client.chat(messages)
print(response.content)
```

## 📖 详细使用指南

### 🔧 CLI 命令详解

#### 交互式聊天
```bash
glm-toolkit chat "你的问题" --temperature 0.7 --max-tokens 500
```

#### 批处理
```bash
# 准备输入文件 (input.json)
# [
#   {"prompt": "问题1"},
#   {"prompt": "问题2"}
# ]

glm-toolkit batch -i input.json -o output.json --workers 5
```

#### 配置管理
```bash
# 查看当前配置
glm-toolkit config --show

# 修改配置
glm-toolkit config --set-model glm-5.1
glm-toolkit config --set-api-url https://custom.api.url
```

#### 缓存管理
```bash
# 查看缓存统计
glm-toolkit cache

# 清空缓存
glm-toolkit cache --clear
```

### 🐍 Python SDK 高级用法

#### 流式响应
```python
for chunk in client.chat_stream(messages):
    print(chunk, end='', flush=True)
```

#### 批处理
```python
results = client.batch_chat([
    "问题1",
    "问题2",
    "问题3"
], show_progress=True)
```

#### 自定义缓存
```python
from glm_toolkit import CacheManager, RateLimiter

cache = CacheManager(ttl=3600)  # 1小时缓存
limiter = RateLimiter(requests=60, period=60)  # 每分钟60请求

client = GLMAPIClient(
    api_key="your_key",
    cache_manager=cache,
    rate_limiter=limiter
)
```

### 🌐 API 代理使用

代理服务兼容 OpenAI API 格式，可直接替换现有应用中的 API 端点：

```bash
# 启动代理
glm-proxy --port 8080 --rate-limit 60

# OpenAI 格式调用
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5.1",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 💡 设计思路与迭代规划

### 🎨 设计理念

1. **模块化架构** - 核心 SDK 独立，CLI 和 Proxy 基于 SDK 构建
2. **配置优先** - 配置文件 + 环境变量 + 命令行参数三层配置
3. **容错设计** - 自动重试、限流保护、优雅降级
4. **性能优先** - 异步处理、连接复用、智能缓存

### 📋 迭代计划

- [ ] v1.1 - 添加 WebSocket 流式支持
- [ ] v1.2 - 增加多 API Key 轮询负载均衡
- [ ] v1.3 - 支持 GLM-4-All 模型
- [ ] v2.0 - Web 管理界面
- [ ] v2.1 - Docker 一键部署

## 📦 打包与部署

### 🐳 Docker 部署

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["glm-proxy", "--host", "0.0.0.0", "--port", "8080"]
```

### ☁️ 云函数部署

```python
# handler.py
from glm_toolkit import GLMAPIClient

def handle(event, context):
    client = GLMAPIClient(api_key=os.environ['GLM_API_KEY'])
    data = json.loads(event.body)
    response = client.chat(data['messages'])
    return {'statusCode': 200, 'body': json.dumps(response.content)}
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

⭐ 如果这个项目对您有帮助，请 star 支持一下！

📧 有问题？欢迎提交 [Issue](https://github.com/gitstq/GLM-5.1-Toolkit/issues)
