---
applyTo:
  - "**/Dockerfile*"
  - "**/compose.yaml"
  - "**/compose.yml"
  - "**/.dockerignore"
  - "**/.devcontainer/**"
---

# Docker / Docker Compose ガイドライン

このファイルはDockerとDocker Composeに関する指示です。

## プロジェクトのDocker構成

このプロジェクトでは以下の3つの環境を提供しています。

- **開発環境**: Docker Compose（`compose.yaml`の`dev`サービス）
- **DevContainer**: VS Code開発コンテナ（`.devcontainer/`）
- **本番環境**: マルチステージビルドの本番イメージ

## Dockerfile

### マルチステージビルド

本番イメージのサイズを最小化するため、マルチステージビルドを使用すること。

```dockerfile
# ビルドステージ
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 本番ステージ
FROM python:3.13-slim AS production
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY ./app ./app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### ベストプラクティス

#### ベースイメージ

- 本番環境: `python:3.13-slim`（軽量）
- 開発環境: `python:3.13`（開発ツール含む）

```dockerfile
# Good（本番用）
FROM python:3.13-slim

# Good（開発用）
FROM python:3.13

# Bad（不必要に大きい）
FROM python:3.13-bullseye
```

#### レイヤーキャッシュの最適化

変更頻度の低いファイルを先にコピーすること。

```dockerfile
# Good（依存関係が変わらない限りキャッシュが効く）
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY ./app ./app

# Bad（アプリコード変更のたびに依存関係を再インストール）
COPY . .
RUN uv sync --frozen
```

#### .dockerignore

不要なファイルをイメージに含めないこと。

```
# .dockerignore
.git
.venv
__pycache__
*.pyc
.pytest_cache
.coverage
.mypy_cache
.ruff_cache
*.db
.env
.vscode
.devcontainer
```

#### 非rootユーザーで実行

セキュリティのため、本番環境では非rootユーザーで実行すること。

```dockerfile
# 本番環境
FROM python:3.13-slim AS production
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser ./app ./app
USER appuser
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### ヘルスチェック

本番イメージにはヘルスチェックを追加すること。

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

## Docker Compose

### 開発環境の設定

`compose.yaml` で開発環境を定義。

```yaml
services:
  dev:
    build:
      context: .
      target: development
    ports:
      - "8000:8000"
    volumes:
      - .:/app  # ホットリロード用
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./test.db
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### ベストプラクティス

#### ボリュームマウント

開発環境ではソースコードをマウントして、変更が即座に反映されるようにすること。

```yaml
services:
  dev:
    volumes:
      - .:/app              # ソースコードをマウント
      - /app/.venv          # 仮想環境はマウントしない（named volumeで永続化）
      - /app/__pycache__    # キャッシュもマウントしない
```

#### 環境変数

機密情報は環境変数で管理。`.env` ファイルを使用すること。

```yaml
services:
  app:
    env_file:
      - .env
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
```

```.env
# .env（Gitには含めない）
DATABASE_URL=postgresql://user:password@db:5432/mydb
SECRET_KEY=your-secret-key
```

#### データベースサービス

開発環境でデータベースを使用する場合の例。

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/mydb

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  db_data:
```

#### ネットワーク

複数のサービス間で通信する場合、カスタムネットワークを定義すること。

```yaml
services:
  app:
    networks:
      - backend

  db:
    networks:
      - backend

networks:
  backend:
    driver: bridge
```

## DevContainer

### 設定ファイル

`.devcontainer/devcontainer.json` でVS Code開発コンテナを設定。

```json
{
  "name": "FastAPI Development",
  "dockerComposeFile": "../compose.yaml",
  "service": "dev",
  "workspaceFolder": "/app",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/app/.venv/bin/python",
        "editor.formatOnSave": true,
        "python.analysis.typeCheckingMode": "basic"
      }
    }
  },
  "postCreateCommand": "uv sync --all-extras"
}
```

### ベストプラクティス

#### VS Code拡張機能

開発に必要な拡張機能を自動インストールすること。

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",           // Python基本機能
        "ms-python.vscode-pylance",   // 型チェック・補完
        "charliermarsh.ruff",         // Ruff統合
        "ms-python.debugpy",          // デバッグ
        "github.copilot"              // GitHub Copilot
      ]
    }
  }
}
```

#### ポートフォワーディング

開発サーバーのポートを自動転送すること。

```json
{
  "forwardPorts": [8000],
  "portsAttributes": {
    "8000": {
      "label": "FastAPI Server",
      "onAutoForward": "notify"
    }
  }
}
```

#### 初期化スクリプト

コンテナ作成後に依存関係をインストールすること。

```json
{
  "postCreateCommand": "uv sync --all-extras && pre-commit install"
}
```

## イメージサイズの最適化

### マルチステージビルドの活用

開発ツールを本番イメージに含めないこと。

```dockerfile
# 開発ステージ（大きい）
FROM python:3.13 AS development
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --all-extras  # 開発依存関係も含む
COPY . .

# 本番ステージ（小さい）
FROM python:3.13-slim AS production
WORKDIR /app
COPY --from=development /app/.venv /app/.venv
COPY ./app ./app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 不要なファイルの除外

`.dockerignore` で不要なファイルを除外すること。

```
# 開発環境ファイル
.devcontainer/
.vscode/
.git/

# Python キャッシュ
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage

# データベース・ログ
*.db
*.log

# 環境変数（機密情報）
.env
.env.local
```

### レイヤー数の削減

複数の `RUN` コマンドを1つにまとめること。

```dockerfile
# Good（1レイヤー）
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Bad（3レイヤー）
RUN apt-get update
RUN apt-get install -y git
RUN apt-get clean
```

## セキュリティ

### ベースイメージの選択

- 公式イメージを使用
- 特定のバージョンタグを指定（`latest` は避ける）
- セキュリティパッチが適用された slim イメージを使用

```dockerfile
# Good
FROM python:3.13-slim

# Bad（脆弱性のリスク）
FROM python:latest
```

### 機密情報の管理

- パスワードやAPIキーをDockerfileにハードコーディングしない
- 環境変数またはDocker Secretsを使用
- `.env` ファイルは `.gitignore` に追加

```dockerfile
# Good
ENV SECRET_KEY=${SECRET_KEY}

# Bad
ENV SECRET_KEY=hardcoded-secret-key-12345
```

### 最小権限の原則

- 非rootユーザーで実行
- 必要最小限のパッケージのみインストール

```dockerfile
FROM python:3.13-slim
RUN useradd -m -u 1000 appuser
USER appuser
WORKDIR /home/appuser/app
```

## デバッグ

### コンテナ内でのデバッグ

DevContainerでは `debugpy` を使用してデバッグ可能。

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
      "jinja": true
    }
  ]
}
```

### ログの確認

```bash
# コンテナのログを確認
docker compose logs -f dev

# 特定のサービスのログ
docker compose logs -f app

# エラーログのみ表示
docker compose logs -f app | grep ERROR
```

## CI/CDでの使用

### イメージビルド

```yaml
# GitHub Actions の例
- name: Build Docker image
  run: docker build -t myapp:${{ github.sha }} --target production .

- name: Run tests in container
  run: docker run --rm myapp:${{ github.sha }} pytest

- name: Push to registry
  run: |
    docker tag myapp:${{ github.sha }} myregistry.com/myapp:latest
    docker push myregistry.com/myapp:latest
```

## コマンドリファレンス

```bash
# Docker Compose
docker compose up dev              # 開発サーバー起動
docker compose up -d               # バックグラウンド起動
docker compose down                # コンテナ停止・削除
docker compose logs -f             # ログ表示
docker compose exec dev bash       # コンテナ内でシェル実行

# Docker（本番イメージ）
docker build -t myapp:latest --target production .  # 本番イメージビルド
docker run -p 8000:8000 myapp:latest                # コンテナ実行
docker images                                        # イメージ一覧
docker ps                                            # 実行中のコンテナ

# DevContainer
# VS Code: Ctrl+Shift+P → "Dev Containers: Reopen in Container"
```

## まとめ

- マルチステージビルドで本番イメージを最適化
- 開発環境はDocker Composeで統一
- DevContainerで一貫した開発体験を提供
- セキュリティを考慮した構成
- `.dockerignore` で不要なファイルを除外
- 環境変数で機密情報を管理
