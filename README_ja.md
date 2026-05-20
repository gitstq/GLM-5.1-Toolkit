# 🌟 GLM-5.1 API ツールキット＆プロキシ

[简体中文](./README_zh-CN.md) | [繁體中文](./README_zh-TW.md) | [English](./README_en.md) | [日本語](./README_ja.md)

---

## 🎉 プロジェクト紹介

**GLM-5.1 API ツールキット＆プロキシ** は、GLM-5.1 モデル専用に設計された総合API管理ツールキットで、Python SDK、CLIツール、APIプロキシサーバーの3つのコア機能を提供します。

### ✨ コアバリュー

🛡️ **プライバシー優先** - ローカルキャッシュで機密データを保護

⚡ **高性能** - インテリジェントキャッシュ＋レート制限でAPIクォータを効率的に活用

🔧 **完全な機能** - SDK / CLI / Proxy三位一体で全ての使用シナリオに対応

🌐 **多言語ドキュメント** - 簡体字中国語、繁体字中国語、English、日本語を完全カバー

### 🎯 GLM-Researcher との補完関係

| プロジェクト | 位置づけ | コア機能 |
|------|------|----------|
| **GLM-Researcher** | 学術ライティングアシスタント | 学術論文の研究と執筆に特化 |
| **GLM-5.1-Toolkit** | API管理ツールキット | API呼び出し、バッチ処理、プロキシサービス |

## ✨ コア機能

- 🐍 **Python SDK** - ストリーミング、バッチ処理、自动リトライ対応のシンプルで使いやすいPythonインターフェース
- 💻 **CLIツール** - 単一コマンドでチャット、バッチ処理、設定管理を完了
- 🌐 **APIプロキシ** - キャッシュとレート制限対応の代理サーバー、OpenAI API互換
- 💾 **インテリジェントキャッシュ** - API応答を自動キャッシュしてクォータを節約し高速化
- ⚡ **レート制限** - APIクォータを保護するインテリジェントなフロー制御アルゴリズム
- 🔄 **自动リトライ** - ネットワーク変動時に自动リトライ、穩定性と信頼性
- 📊 **統計監視** - リアルタイムの使用状況とキャッシュヒット率を表示
- 🧩 **モジュール設計** - 柔軟に組み合わせ、必要なものだけを可以使用

## 🚀 クイックスタート

### 📦 インストール

```bash
# pipでインストール
pip install glm-api-toolkit

# ソースからインストール
git clone https://github.com/gitstq/GLM-5.1-Toolkit.git
cd GLM-5.1-Toolkit
pip install -e .
```

### ⚙️ API Keyの設定

```bash
# 環境変数を設定
export GLM_API_KEY=your_api_key_here

# またはCLIで設定
glm-toolkit config --set-api-key your_api_key_here
```

### 💬 クイックチャット

```bash
glm-toolkit chat "こんにちは、GLM-5.1モデルを紹介してください"
```

### 🌐 プロキシサーバーの起動

```bash
glm-proxy --port 8080
```

### 📝 Python SDKの使用

```python
from glm_toolkit import GLMAPIClient

# クライアントを初期化
client = GLMAPIClient(api_key="your_api_key")

# シンプルなチャット
response = client.simple_chat("こんにちは、GLM！")
print(response)

# コンテキスト付きチャット
messages = [
    {"role": "system", "content": "あなたは経験豊富なPythonプログラマーです"},
    {"role": "user", "content": "クイックソートを実装するには？"}
]
response = client.chat(messages)
print(response.content)
```

## 📖 詳細な使用ガイド

### 🔧 CLIコマンドの詳細

#### インタラクティブチャット
```bash
glm-toolkit chat "あなたの質問" --temperature 0.7 --max-tokens 500
```

#### バッチ処理
```bash
# 入力ファイルを準備 (input.json)
# [
#   {"prompt": "質問1"},
#   {"prompt": "質問2"}
# ]

glm-toolkit batch -i input.json -o output.json --workers 5
```

#### 設定管理
```bash
# 現在の設定を表示
glm-toolkit config --show

# 設定を更新
glm-toolkit config --set-model glm-5.1
glm-toolkit config --set-api-url https://custom.api.url
```

#### キャッシュ管理
```bash
# キャッシュ統計を表示
glm-toolkit cache

# キャッシュをクリア
glm-toolkit cache --clear
```

### 🐍 Python SDK 上級用法

#### ストリーミング応答
```python
for chunk in client.chat_stream(messages):
    print(chunk, end='', flush=True)
```

#### バッチ処理
```python
results = client.batch_chat([
    "質問1",
    "質問2",
    "質問3"
], show_progress=True)
```

#### カスタムキャッシュ
```python
from glm_toolkit import CacheManager, RateLimiter

cache = CacheManager(ttl=3600)  # 1時間キャッシュ
limiter = RateLimiter(requests=60, period=60)  # 毎分60リクエスト

client = GLMAPIClient(
    api_key="your_key",
    cache_manager=cache,
    rate_limiter=limiter
)
```

### 🌐 APIプロキシの使用

プロキシサービスはOpenAI APIフォーマットと互換性があり、既存アプリケーションのAPIエンドポイントを直接置き換え可能：

```bash
# プロキシを起動
glm-proxy --port 8080 --rate-limit 60

# OpenAIフォーマットで呼叫
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5.1",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 💡 設計思想とロードマップ

### 🎨 設計原則

1. **モジュール設計** - コアSDKは独立、CLIとProxyはSDKに基づいて構築
2. **設定優先** - 設定ファイル＋環境変数＋コマンドライン引数の3層設定
3. **フォールトトレランス** - 自动リトライ、レート制限保護、グレースフルデグラデーション
4. **パフォーマンス優先** - 非同期処理、接続再利用、インテリジェントキャッシュ

### 📋 ロードマップ

- [ ] v1.1 - WebSocketストリーミング対応を追加
- [ ] v1.2 - 複数API Keyの負荷分散を追加
- [ ] v1.3 - GLM-4-Allモデルのサポート
- [ ] v2.0 - Web管理インターフェース
- [ ] v2.1 - Dockerワンクリックデプロイ

## 📦 パッケージングとデプロイ

### 🐳 Dockerデプロイ

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["glm-proxy", "--host", "0.0.0.0", "--port", "8080"]
```

### ☁️ クラウド関数デプロイ

```python
# handler.py
from glm_toolkit import GLMAPIClient

def handle(event, context):
    client = GLMAPIClient(api_key=os.environ['GLM_API_KEY'])
    data = json.loads(event.body)
    response = client.chat(data['messages'])
    return {'statusCode': 200, 'body': json.dumps(response.content)}
```

## 🤝 コントリビューション

IssueとPull Requestを歓迎します！

1. リポジトリをFork
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 📄 ライセンス

このプロジェクトは[MIT License](LICENSE)の下でライセンスされています。

---

⭐ このプロジェクトが役立った場合は、starしてください！

📧 質問がありますか？[Issue](https://github.com/gitstq/GLM-5.1-Toolkit/issues)を開くか、お気軽にどうぞ
