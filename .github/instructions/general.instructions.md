---
applyTo:
  - "**/*.md"
  - "**/.gitignore"
  - "**/.github/workflows/**"
  - "**/renovate.json"
  - "**/.vscode/**"
---

# 一般的な開発ガイドライン

このファイルはPythonやDocker以外の一般的な開発プラクティスに関する指示です。

## プロジェクト概要

Python 3.13とFastAPIを使用したWebアプリケーションプロジェクト。

- **フレームワーク**: FastAPI
- **データベース**: SQLAlchemy（非同期）、Alembic（マイグレーション）
- **パッケージ管理**: uv
- **開発環境**: DevContainer、Docker Compose

## Git ワークフロー

### ブランチ戦略

このプロジェクトのブランチ構成：

- `feature/add-ci`: メインブランチ（PRのベース）
- `chore/*`: 雑務・設定変更用
- `feature/*`: 新機能開発用
- `fix/*`: バグ修正用

### コミットメッセージ

**フォーマット**

```
<type>: <subject>

<body>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Type**

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメントのみの変更
- `style`: コードの意味に影響しない変更（空白、フォーマット）
- `refactor`: バグ修正でも機能追加でもないコード変更
- `test`: テストの追加・修正
- `chore`: ビルドプロセスやツールの変更
- `perf`: パフォーマンス改善

**例**

```
feat: タスク検索機能を追加

タイトルと説明でタスクを検索できる機能を実装。
フルテキスト検索をサポート。

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

```
fix: タスク削除時の404エラーを修正

存在しないタスクを削除しようとした際に、
404エラーを正しく返すように修正。

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

```
chore: Renovateの設定を追加

自動依存関係更新のためのRenovate設定ファイルを追加。

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

### pre-commit フック

コミット前に自動的にチェックが実行されます（`.pre-commit-config.yaml`）。

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

**フックが失敗した場合**

1. 自動修正された内容を確認
2. 再度ステージングに追加: `git add .`
3. 再度コミット: `git commit`

## プルリクエスト

### 作成前のチェックリスト

- [ ] すべてのテストが通る: `uv task test`
- [ ] 型チェックが通る: `uv task type`
- [ ] Lintが通る: `uv task lint-check`
- [ ] フォーマットが正しい: `uv task fmt-check`
- [ ] 新しい機能にはテストを追加済み

### PRテンプレート

```markdown
## 概要
この変更の目的と内容を簡潔に説明

## 変更内容
- 変更点1
- 変更点2

## テスト
- [ ] ユニットテストを追加
- [ ] インテグレーションテストを追加
- [ ] 手動でテスト済み

## 影響範囲
この変更が影響する部分
```

### レビュー観点

- コードの可読性
- 型安全性
- テストカバレッジ
- パフォーマンスへの影響
- セキュリティの考慮

## CI/CD

### GitHub Actions

プロジェクトではCI/CDパイプラインを設定することを推奨。

**基本的なワークフロー**

```yaml
name: CI

on:
  push:
    branches: [main, feature/*]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v1

      - name: Set up Python
        run: uv python install 3.13

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Run linter
        run: uv run ruff check .

      - name: Run formatter check
        run: uv run ruff format --check .

      - name: Run type check
        run: uv run mypy app

      - name: Run tests
        run: uv run pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Renovate

依存関係の自動更新には Renovate を使用（`renovate.json`）。

```json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    }
  ]
}
```

## ドキュメント

### README.md

以下の内容を含めること：

- プロジェクトの概要
- セットアップ手順（DevContainer、ローカル、Docker）
- 実行方法
- テスト方法
- プロジェクト構造
- 開発ワークフロー

### API ドキュメント

FastAPIの自動生成ドキュメントを活用。

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

エンドポイントには必ずdocstringを記述すること。

```python
@app.post("/tasks/", response_model=Task, status_code=201)
async def create_task(
    task: TaskCreate,
    session: AsyncSession = Depends(get_session)
) -> Task:
    """
    新しいタスクを作成する。

    - **title**: タスクのタイトル（必須）
    - **description**: タスクの説明（オプション）
    """
    return await crud_task.create_task(session, task)
```

## セキュリティ

### 機密情報の管理

**環境変数を使用**

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
```

**`.env` ファイル（Gitには含めない）**

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/mydb
SECRET_KEY=your-secret-key-here
```

**`.gitignore` に追加**

```
.env
.env.local
.env.production
*.pem
*.key
```

### 脆弱性チェック

定期的に依存関係の脆弱性をチェックすること。

```bash
# pipで脆弱性チェック
pip-audit

# またはRenovateの自動更新を活用
```

### HTTPS/SSL

本番環境では必ずHTTPSを使用すること。

## パフォーマンス

### 【最重要】非同期処理によるパフォーマンス向上

**FastAPIで最も重要なパフォーマンス最適化は非同期処理です。**

すべてのI/O操作（データベース、HTTP、ファイル、外部API）を非同期で実装することで、**スループットが10倍〜100倍向上**します。

**必ず非同期にすべき操作**

- ✅ データベースクエリ（AsyncSession）
- ✅ HTTPリクエスト（httpx.AsyncClient）
- ✅ ファイル読み書き（aiofiles）
- ✅ Redis/キャッシュ（aioredis）
- ✅ 外部API呼び出し（非同期クライアント）
- ✅ メッセージキュー操作
- ✅ 重い計算処理（asyncio.to_thread()）

**パフォーマンスへの影響例**

```python
# 同期処理（悪い - 10 req/sec）
def get_user_data(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()  # 100ms ブロック
    return user

# 非同期処理（良い - 1000 req/sec）
async def get_user_data(user_id: int):
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

詳細は `python.md` の「非同期処理」セクションを参照してください。

### データベースクエリの最適化

#### N+1問題の回避

`selectinload` または `joinedload` を使用してeager loadingを実装すること。

```python
# Good（eager loading - 1クエリ）
result = await session.execute(
    select(User).options(selectinload(User.tasks))
)
users = result.scalars().all()
for user in users:
    print(user.tasks)  # 追加のクエリなし

# Bad（N+1問題 - N+1クエリ）
users = await session.execute(select(User))
for user in users.scalars():
    # 各ユーザーごとにクエリが発行される（遅い）
    tasks = await session.execute(
        select(Task).where(Task.user_id == user.id)
    )
```

#### インデックスの設定

頻繁に検索・ソートするカラムにはインデックスを設定すること。

```python
from sqlalchemy import Index

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)  # インデックス
    status: Mapped[str] = mapped_column(index=True)   # インデックス
    created_at: Mapped[datetime] = mapped_column(index=True)

    # 複合インデックス
    __table_args__ = (
        Index('ix_user_status', 'user_id', 'status'),
    )
```

#### 必要なカラムのみ取得

`load_only` や `defer` で不要なカラムを除外すること。

```python
# Good（必要なカラムのみ）
result = await session.execute(
    select(User).options(load_only(User.id, User.name))
)

# Bad（全カラムを取得 - 大きなBLOBカラムがある場合に遅い）
result = await session.execute(select(User))
```

### キャッシュ

頻繁にアクセスされる変更の少ないデータはキャッシュすること。

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_settings() -> Settings:
    """設定を取得（キャッシュ）。"""
    return Settings()
```

**Redis等の外部キャッシュを使用する場合**

```python
import aioredis

async def get_user_cached(user_id: int, session: AsyncSession) -> User | None:
    redis = await aioredis.from_url("redis://localhost")

    # キャッシュを確認
    cached = await redis.get(f"user:{user_id}")
    if cached:
        return User.parse_raw(cached)

    # DBから取得
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        # キャッシュに保存（5分間）
        await redis.setex(f"user:{user_id}", 300, user.json())

    return user
```

### 並行処理

複数の独立したI/O操作は `asyncio.gather()` で並行実行すること。

```python
import asyncio

# Good（並行実行 - 速い）
async def get_dashboard(user_id: int, session: AsyncSession):
    user, tasks, stats = await asyncio.gather(
        get_user(session, user_id),
        get_tasks(session, user_id),
        get_statistics(session, user_id)
    )
    return {"user": user, "tasks": tasks, "stats": stats}

# Bad（逐次実行 - 遅い）
async def get_dashboard(user_id: int, session: AsyncSession):
    user = await get_user(session, user_id)
    tasks = await get_tasks(session, user_id)
    stats = await get_statistics(session, user_id)
    return {"user": user, "tasks": tasks, "stats": stats}
```

## ログ

### ログレベル

- `DEBUG`: 開発時のデバッグ情報
- `INFO`: 一般的な情報（リクエスト、処理完了など）
- `WARNING`: 警告（非推奨の使用、リトライなど）
- `ERROR`: エラー（例外、失敗など）
- `CRITICAL`: 致命的なエラー（システム停止など）

### ロギング設定

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@app.post("/tasks/")
async def create_task(task: TaskCreate) -> Task:
    logger.info(f"Creating task: {task.title}")
    try:
        result = await crud_task.create_task(session, task)
        logger.info(f"Task created: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise
```

### 本番環境でのログ

- JSON形式でログを出力
- ログ集約サービス（CloudWatch、Datadog など）に送信
- 機密情報をログに含めない

## モニタリング

### ヘルスチェックエンドポイント

```python
@app.get("/health")
async def health_check() -> dict[str, str]:
    """ヘルスチェックエンドポイント。"""
    # データベース接続確認
    try:
        await session.execute(select(1))
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
```

### メトリクス

Prometheusなどを使用してメトリクスを収集することを推奨。

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## エラーハンドリング

### カスタム例外ハンドラー

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """ValueErrorのカスタムハンドラー。"""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

## 開発環境

### VS Code 設定

推奨設定（`.vscode/settings.json`）：

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.analysis.typeCheckingMode": "basic",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

### エディタ拡張機能

推奨する VS Code 拡張機能：

- `ms-python.python`: Python基本機能
- `ms-python.vscode-pylance`: 型チェック・補完
- `charliermarsh.ruff`: Ruff統合
- `ms-python.debugpy`: デバッグ
- `github.copilot`: GitHub Copilot

## トラブルシューティング

### よくある問題

**Python 3.13が見つからない**

```bash
uv python list
uv python install 3.13
```

**依存関係のインストールに失敗**

```bash
uv sync --reinstall
```

**テストが失敗する**

```bash
# キャッシュをクリア
rm -rf .pytest_cache
pytest --cache-clear
```

**型チェックエラー**

```bash
# mypyのキャッシュをクリア
rm -rf .mypy_cache
uv task type
```

## リソース

### 公式ドキュメント

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [uv](https://docs.astral.sh/uv/)
- [Ruff](https://docs.astral.sh/ruff/)

### コミュニティ

- GitHub Issues: プロジェクトのIssueトラッカー
- プルリクエスト: コントリビューション歓迎

## まとめ

- 明確なGitワークフローを維持
- CI/CDで品質を自動チェック
- セキュリティを最優先
- ドキュメントを常に最新に保つ
- パフォーマンスとモニタリングを意識
- 一貫した開発環境を提供
