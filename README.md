# FastAPI Development Environment

Python 3.13系を使用した FastAPI の開発環境です。

## 機能

- **Python**: 3.13
- **FastAPI**: 高速な Web フレームワーク
- **uv**: 高速な Python パッケージマネージャー
- **taskipy**: Python タスクランナー
- **Ruff**: 高速な Python リンター・フォーマッター
- **mypy**: 静的型チェッカー
- **pytest**: テストフレームワーク
- **DevContainer**: 統一された開発環境

## セットアップ

### DevContainer でのセットアップ（推奨）

VS Code の DevContainer 拡張機能を使用：

1. VS Code で以下のいずれかを実行：
   - Ctrl+Shift+P → 「Dev Containers: Reopen in Container」
   - フォルダ内の `.devcontainer/devcontainer.json` ファイルを検出して自動提案
   - 左下のリモートインジケータをクリック → 「Reopen in Container」

2. 自動的に開発用 Docker イメージがビルドされます（初回のみ数分）

3. コンテナ内で自動的に起動：
   - Python 3.13 環境
   - uvicorn で `http://localhost:8000` でサーバー起動
   - ターミナルで `uv` コマンドが使用可能
   - VS Code 拡張機能（Pylance, Ruff など）が自動インストール

4. コンテナから抜ける場合：
   - VS Code 左下の「Dev Container: FastAPI Development」をクリック → 「Reopen Locally」

### ローカルセットアップ（uvを使用）

```bash
# Python 3.13 がインストールされていることを確認
python3 --version

# uv をインストール（未インストール時）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係をインストール
uv sync --all-extras

# 環境をアクティベート
source .venv/bin/activate
```

### Docker でのセットアップ

#### 開発環境（自動リロード付き）

```bash
# イメージをビルドして起動
docker compose up dev

# or 別ターミナルから
docker compose run --rm dev uv run pytest

# コンテナを停止
docker compose down
```

開発サーバーは `http://localhost:8000` で起動します。

#### 本番イメージのビルド・実行

```bash
# 本番イメージをビルド（圧縮版）
docker build -t fastapi-app:latest --target production .

# イメージサイズを確認
docker images fastapi-app

# 実行
docker run -p 8001:8000 fastapi-app:latest
```

サーバーは `http://localhost:8001` で起動します。

## 実行

### 開発サーバーの起動

```bash
# 方法1: 直接実行
python main.py

# 方法2: uvicorn で実行（自動リロード）
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

サーバーは `http://localhost:8000` で起動します。

### テスト実行

```bash
# 全テストを実行
uv task test

# ユニットテストのみ実行
uv task test-unit

# インテグレーションテストのみ実行
uv task test-integration
```

### コード品質チェック

```bash
# 自動フォーマット（修正）
uv task fmt

# フォーマットのチェック（修正なし）
uv task fmt-check

# リント修正
uv task lint

# リントチェック（修正なし）
uv task lint-check

# 型チェック
uv task type

# 全チェック実行（fmt-check, lint-check, type, test）
uv task check
```

## プロジェクト構造

```tree
.
├── Dockerfile                      # マルチステージビルド
├── compose.yml                     # Docker Compose 設定
├── main.py                         # メインアプリケーション
├── tests/
│   ├── conftest.py                # 共通テスト設定（TestClient fixture）
│   ├── unit/                       # ユニットテスト
│   │   ├── conftest.py
│   │   └── test_main_utils.py
│   └── integration/                # インテグレーションテスト
│       ├── conftest.py
│       ├── test_root.py            # GET / のテスト
│       ├── test_health.py          # GET /health のテスト
│       └── test_add.py             # GET /add のテスト
├── .devcontainer/                  # DevContainer 設定
│   └── devcontainer.json
├── pyproject.toml                  # プロジェクト設定（taskipy, pytest, ruff, mypy）
├── .gitignore
└── README.md
```

## Docker イメージサイズの比較

```bash
# 開発ステージ（開発用）
# - Python 3.13
# - pip, uv
# - pytest, ruff など開発ツール
# - ソースコード全て

# 本番ステージ（プロダクション用）
# - Python 3.13 (slim)
# - 必要なランタイムのみ
# - アプリケーションコードのみ
# → 本番版はサイズが大幅に削減
```

## 開発ワークフロー

1. コードを編集
2. 自動保存時にフォーマット（VS Code 設定で有効）
3. すべてのチェックを実行: `uv task check`
4. サーバーで動作確認: `python main.py`

### taskipy コマンド一覧

| コマンド | 説明 |
|---------|------|
| `uv task fmt` | Ruff でフォーマット（修正） |
| `uv task fmt-check` | Ruff でフォーマットチェック（修正なし） |
| `uv task lint` | Ruff リント（修正） |
| `uv task lint-check` | Ruff リントチェック（修正なし） |
| `uv task type` | mypy で型チェック |
| `uv task test` | pytest で全テスト実行 |
| `uv task test-unit` | ユニットテストのみ実行 |
| `uv task test-integration` | インテグレーションテストのみ実行 |
| `uv task check` | 全チェック実行（推奨）|

## トラブルシューティング

### Python 3.13 が見つからない場合

```bash
# uv でサポートされているバージョンを確認
uv python list

# 必要に応じて Python をインストール
uv python install 3.13
```

### DevContainer がビルドに失敗した場合

1. DevContainer を削除: Ctrl+Shift+P → "Dev Containers: Delete"
2. 再度開く: Ctrl+Shift+P → "Dev Containers: Reopen in Container"
