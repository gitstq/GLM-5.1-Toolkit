# 🌟 GLM-5.1 API 工具包與代理伺服器

[简体中文](./README_zh-CN.md) | [繁體中文](./README_zh-TW.md) | [English](./README_en.md) | [日本語](./README_ja.md)

---

## 🎉 專案介紹

**GLM-5.1 API 工具包與代理伺服器** 是一款專為 GLM-5.1 模型打造的綜合 API 管理工具包，提供 Python SDK、命令列工具和 API 代理伺服器三大核心功能。

### ✨ 核心價值

🛡️ **隱私優先** - 本地快取，敏感資料不外洩

⚡ **效能卓越** - 智慧快取 + 速率限制，高效利用 API 配額

🔧 **功能完整** - SDK / CLI / Proxy 三位一體，滿足所有使用場景

🌐 **多語言文件** - 簡體中文、繁體中文、English、日本語全方位覆蓋

### 🎯 與 GLM-Researcher 的互補關係

| 專案 | 定位 | 核心功能 |
|------|------|----------|
| **GLM-Researcher** | 學術寫作助手 | 專注於學術論文研究與寫作 |
| **GLM-5.1-Toolkit** | API 管理工具包 | API 呼叫、批次處理、代理服務 |

## ✨ 核心特性

- 🐍 **Python SDK** - 簡潔易用的 Python 介面，支持串流回應、批次處理、自动重试
- 💻 **CLI 工具** - 一行命令完成聊天、批次處理、配置管理
- 🌐 **API 代理** - 支持快取、速率限制的代理伺服器，兼容 OpenAI API 格式
- 💾 **智慧快取** - 自動快取 API 回應，節省配額加速存取
- ⚡ **速率限制** - 智慧限流演算法，保護 API 配額
- 🔄 **自動重試** - 網路波動自動重試，穩定可靠
- 📊 **統計監控** - 即時查看使用情況與快取命中率
- 🧩 **模組化設計** - 靈活組合，按需使用

## 🚀 快速開始

### 📦 安裝

```bash
# 使用 pip 安裝
pip install glm-api-toolkit

# 或從原始碼安裝
git clone https://github.com/gitstq/GLM-5.1-Toolkit.git
cd GLM-5.1-Toolkit
pip install -e .
```

### ⚙️ 配置 API Key

```bash
# 設定環境變數
export GLM_API_KEY=your_api_key_here

# 或使用 CLI 配置
glm-toolkit config --set-api-key your_api_key_here
```

### 💬 快速聊天

```bash
glm-toolkit chat "你好，請介紹一下GLM-5.1模型"
```

### 🌐 啟動代理服務

```bash
glm-proxy --port 8080
```

### 📝 Python SDK 使用

```python
from glm_toolkit import GLMAPIClient

# 初始化客戶端
client = GLMAPIClient(api_key="your_api_key")

# 簡單聊天
response = client.simple_chat("你好，GLM！")
print(response)

# 帶上下文的聊天
messages = [
    {"role": "system", "content": "你是一個專業的Python程式員"},
    {"role": "user", "content": "如何實現快速排序？"}
]
response = client.chat(messages)
print(response.content)
```

## 📖 詳細使用指南

### 🔧 CLI 命令詳解

#### 互動式聊天
```bash
glm-toolkit chat "你的問題" --temperature 0.7 --max-tokens 500
```

#### 批次處理
```bash
# 準備輸入檔案 (input.json)
# [
#   {"prompt": "問題1"},
#   {"prompt": "問題2"}
# ]

glm-toolkit batch -i input.json -o output.json --workers 5
```

#### 配置管理
```bash
# 查看當前配置
glm-toolkit config --show

# 修改配置
glm-toolkit config --set-model glm-5.1
glm-toolkit config --set-api-url https://custom.api.url
```

#### 快取管理
```bash
# 查看快取統計
glm-toolkit cache

# 清空快取
glm-toolkit cache --clear
```

### 🐍 Python SDK 進階用法

#### 串流回應
```python
for chunk in client.chat_stream(messages):
    print(chunk, end='', flush=True)
```

#### 批次處理
```python
results = client.batch_chat([
    "問題1",
    "問題2",
    "問題3"
], show_progress=True)
```

#### 自訂快取
```python
from glm_toolkit import CacheManager, RateLimiter

cache = CacheManager(ttl=3600)  # 1小時快取
limiter = RateLimiter(requests=60, period=60)  # 每分鐘60請求

client = GLMAPIClient(
    api_key="your_key",
    cache_manager=cache,
    rate_limiter=limiter
)
```

### 🌐 API 代理使用

代理服務兼容 OpenAI API 格式，可直接替換現有應用中的 API 端點：

```bash
# 啟動代理
glm-proxy --port 8080 --rate-limit 60

# OpenAI 格式呼叫
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5.1",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 💡 設計思路與迭代規劃

### 🎨 設計理念

1. **模組化架構** - 核心 SDK 獨立，CLI 和 Proxy 基於 SDK 構建
2. **配置優先** - 設定檔 + 環境變數 + 命令列參數三層配置
3. **容錯設計** - 自動重試、限流保護、優雅降級
4. **效能優先** - 非同步處理、連線復用、智慧快取

### 📋 迭代計畫

- [ ] v1.1 - 添加 WebSocket 串流支持
- [ ] v1.2 - 增加多 API Key 輪詢負載均衡
- [ ] v1.3 - 支持 GLM-4-All 模型
- [ ] v2.0 - Web 管理介面
- [ ] v2.1 - Docker 一鍵部署

## 📦 包裝與部署

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

### ☁️ 雲端函數部署

```python
# handler.py
from glm_toolkit import GLMAPIClient

def handle(event, context):
    client = GLMAPIClient(api_key=os.environ['GLM_API_KEY'])
    data = json.loads(event.body)
    response = client.chat(data['messages'])
    return {'statusCode': 200, 'body': json.dumps(response.content)}
```

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 本倉庫
2. 創建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立 Pull Request

## 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

⭐ 如果這個專案對您有幫助，請 star 支持一下！

📧 有問題？歡迎提交 [Issue](https://github.com/gitstq/GLM-5.1-Toolkit/issues)
