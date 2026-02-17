---
applyTo:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/alembic.ini"
  - "**/.pre-commit-config.yaml"
---

# Python コーディング規約

このファイルはPythonコードに関する指示です。

## 使用バージョン

- **Python**: 3.13
- Python 3.13の新機能を積極的に活用する

## 型ヒント

### 必須事項

すべての関数・メソッドに型ヒントを付けること（mypy strict設定）。

```python
# Good
def get_user(user_id: int) -> User | None:
    """ユーザーをIDで取得する。"""
    return db.query(User).filter(User.id == user_id).first()

# Bad（型ヒントがない）
def get_user(user_id):
    return db.query(User).filter(User.id == user_id).first()
```

### モダンな型記法

Python 3.10+の新しい型記法を使用すること。

```python
# Good（Python 3.10+）
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Bad（古い記法）
from typing import List, Dict
def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}
```

### Optional vs Union

Python 3.10+の `|` 記法を使用。

```python
# Good
def find_task(task_id: int) -> Task | None:
    pass

# Bad
from typing import Optional
def find_task(task_id: int) -> Optional[Task]:
    pass
```

## 非同期処理 【重要：パフォーマンスの鍵】

### なぜ非同期処理が必須なのか

**パフォーマンスへの影響**

同期的なI/O処理は、処理が完了するまでスレッド全体をブロックします。FastAPIは単一のイベントループで複数のリクエストを並行処理するため、**1つのブロッキング処理が全体のパフォーマンスを大幅に低下させます**。

```python
# 同期処理の場合（悪い例）
# データベースクエリに100msかかる場合、その間他のリクエストは待機
def get_task(task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()  # 100ms ブロック

# 非同期処理の場合（良い例）
# I/O待機中に他のリクエストを処理できる
async def get_task(task_id: int):
    return await db.execute(select(Task).where(Task.id == task_id))  # 100ms 待機（他の処理が可能）
```

**具体的な数値例**

- 同期処理: 100リクエスト/秒 → 各リクエスト100ms → スループット: 10 req/sec
- 非同期処理: 100リクエスト/秒 → 各リクエスト100ms → スループット: 1000 req/sec（理論値）

### 必ず非同期にすべきI/O操作

以下のすべての操作は**必ず非同期**で実装すること（パフォーマンス劣化の原因）：

1. **データベース操作** - SQLAlchemy AsyncSession
2. **HTTPリクエスト** - httpx.AsyncClient
3. **ファイルI/O** - aiofiles
4. **外部API呼び出し** - 非同期クライアントライブラリ
5. **Redis/キャッシュ** - aioredis, aiocache
6. **メッセージキュー** - aiokafka, aio-pika
7. **時間のかかる計算** - asyncio.to_thread()

### FastAPIエンドポイント

**必須ルール**: すべてのエンドポイントを `async def` で定義すること。

```python
# Good（非同期 - パフォーマンスが高い）
@app.get("/tasks/{task_id}")
async def read_task(
    task_id: int,
    session: AsyncSession = Depends(get_session)
) -> TaskSchema:
    # I/O待機中に他のリクエストを処理できる
    task = await crud.get_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Bad（同期 - 他のリクエストをブロックする）
@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    # この処理中、サーバー全体が待機状態になる
    return crud.get_task(task_id)
```

### データベース操作

**必須ルール**: SQLAlchemyは `AsyncSession` を使用し、すべてのDB操作を `await` すること。

```python
# Good（非同期DB操作）
async def create_task(session: AsyncSession, task: TaskCreate) -> Task:
    db_task = Task(**task.model_dump())
    session.add(db_task)
    await session.commit()      # I/O待機中に他の処理が可能
    await session.refresh(db_task)
    return db_task

async def get_tasks(session: AsyncSession, limit: int = 100) -> list[Task]:
    result = await session.execute(
        select(Task).limit(limit)
    )
    return list(result.scalars().all())

# Bad（同期DB操作 - 絶対に避ける）
def create_task(session: Session, task: TaskCreate) -> Task:
    db_task = Task(**task.dict())
    session.add(db_task)
    session.commit()  # ブロッキング！他のリクエストが待機
    return db_task
```

### HTTPリクエスト

外部APIへのリクエストは**必ず非同期クライアント**を使用すること。

```python
import httpx

# Good（非同期HTTPリクエスト）
async def fetch_external_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)  # 外部API待機中に他の処理が可能
        return response.json()

# Bad（同期HTTPリクエスト - 絶対に避ける）
import requests

def fetch_external_data(url: str) -> dict:
    response = requests.get(url)  # ブロッキング！最大数秒間待機
    return response.json()
```

### ファイルI/O

ファイル操作は `aiofiles` を使用すること。

```python
import aiofiles

# Good（非同期ファイル読み書き）
async def read_file(path: str) -> str:
    async with aiofiles.open(path, mode="r") as f:
        return await f.read()  # I/O待機中に他の処理が可能

async def write_log(path: str, content: str) -> None:
    async with aiofiles.open(path, mode="a") as f:
        await f.write(f"{content}\n")

# Bad（同期ファイルI/O - 避ける）
def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()  # ディスクI/O中ブロック
```

### CPU集約的な処理

重い計算処理は `asyncio.to_thread()` でスレッドプールに委譲すること。

```python
import asyncio
import hashlib

# Good（CPU集約的処理を別スレッドで実行）
async def hash_password(password: str) -> str:
    def _hash():
        return hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()

    # 計算中に他のリクエストを処理できる
    return await asyncio.to_thread(_hash)

# Bad（メインスレッドで重い計算 - 避ける）
def hash_password(password: str) -> str:
    # 計算中、他のリクエストがブロックされる
    return hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()
```

### 複数の非同期操作を並行実行

複数のI/O操作は `asyncio.gather()` で並行実行すること（パフォーマンス向上）。

```python
import asyncio

# Good（並行実行 - 高速）
async def get_user_dashboard(user_id: int, session: AsyncSession) -> Dashboard:
    # 3つのDB操作を並行実行（合計時間 = max(各操作の時間)）
    user, tasks, notifications = await asyncio.gather(
        crud.get_user(session, user_id),
        crud.get_user_tasks(session, user_id),
        crud.get_user_notifications(session, user_id)
    )
    return Dashboard(user=user, tasks=tasks, notifications=notifications)

# Bad（逐次実行 - 遅い）
async def get_user_dashboard(user_id: int, session: AsyncSession) -> Dashboard:
    # 合計時間 = 各操作の時間の合計（3倍遅い）
    user = await crud.get_user(session, user_id)
    tasks = await crud.get_user_tasks(session, user_id)
    notifications = await crud.get_user_notifications(session, user_id)
    return Dashboard(user=user, tasks=tasks, notifications=notifications)
```

## Docstring

### 基本ルール

- すべての関数・クラスに**日本語**のdocstringを記述
- 1行の簡潔な説明（関数の目的を動詞で開始）
- 詳細な説明が必要な場合のみ複数行記述

```python
def calculate_total_price(items: list[Item], tax_rate: float) -> float:
    """商品リストの合計金額を税込みで計算する。"""
    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate)
```

### 複雑な関数の場合

```python
async def process_payment(
    user_id: int,
    amount: float,
    payment_method: str
) -> PaymentResult:
    """
    支払い処理を実行する。

    支払いゲートウェイとの通信、トランザクション記録、
    ユーザー残高の更新を行う。

    Args:
        user_id: ユーザーID
        amount: 支払い金額
        payment_method: 支払い方法（"card", "bank"など）

    Returns:
        支払い結果（成功/失敗、トランザクションIDなど）

    Raises:
        InsufficientFundsError: 残高不足の場合
        PaymentGatewayError: 決済サービスとの通信エラー
    """
    ...
```

## FastAPI

### プロジェクト構造

```
app/
├── main.py         # アプリケーションエントリーポイント、lifespan管理
├── models/         # SQLAlchemyモデル（テーブル定義）
├── schemas/        # Pydanticスキーマ（リクエスト/レスポンス型）
├── crud/           # CRUD操作（データベース操作ロジック）
└── routers/        # APIエンドポイント定義
```

### レイヤー分離

各層の責務を明確に分けること。

**routers/**（エンドポイント層）
- HTTPリクエスト/レスポンスの処理
- バリデーション（Pydanticで自動）
- CRUD層の呼び出し

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import task as crud_task
from app.schemas.task import Task, TaskCreate
from app.models.base import get_session

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task, status_code=201)
async def create_task(
    task: TaskCreate,
    session: AsyncSession = Depends(get_session)
) -> Task:
    """新しいタスクを作成する。"""
    return await crud_task.create_task(session, task)
```

**crud/**（ビジネスロジック層）
- データベース操作
- ビジネスロジック
- データの変換

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate

async def create_task(session: AsyncSession, task: TaskCreate) -> Task:
    """タスクをデータベースに作成する。"""
    db_task = Task(**task.model_dump())
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task

async def get_task(session: AsyncSession, task_id: int) -> Task | None:
    """タスクをIDで取得する。"""
    result = await session.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()
```

**schemas/**（データ型定義）
- Pydanticモデル
- リクエスト/レスポンスの型

```python
from pydantic import BaseModel, ConfigDict

class TaskBase(BaseModel):
    """タスクの基本スキーマ。"""
    title: str
    description: str | None = None

class TaskCreate(TaskBase):
    """タスク作成リクエストスキーマ。"""
    pass

class Task(TaskBase):
    """タスクレスポンススキーマ。"""
    id: int
    completed: bool

    model_config = ConfigDict(from_attributes=True)
```

**models/**（データベースモデル）
- SQLAlchemyモデル
- テーブル定義

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class Task(Base):
    """タスクテーブル。"""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500))
    completed: Mapped[bool] = mapped_column(default=False)
```

### エラーハンドリング

FastAPIの `HTTPException` を使用し、適切なステータスコードを返すこと。

```python
from fastapi import HTTPException

# 404 Not Found
if not task:
    raise HTTPException(status_code=404, detail="Task not found")

# 400 Bad Request
if amount < 0:
    raise HTTPException(status_code=400, detail="Amount must be positive")

# 403 Forbidden
if user.id != resource.owner_id:
    raise HTTPException(status_code=403, detail="Not authorized")

# 409 Conflict
if existing_user:
    raise HTTPException(status_code=409, detail="User already exists")
```

## SQLAlchemy 2.0+

### モデル定義

SQLAlchemy 2.0+の新しい `Mapped` 記法を使用すること。

```python
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)

    # リレーション
    tasks: Mapped[list["Task"]] = relationship(back_populates="user")

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # リレーション
    user: Mapped["User"] = relationship(back_populates="tasks")
```

### クエリ

SQLAlchemy 2.0+の `select()` スタイルを使用すること（レガシーなQuery APIは使わない）。

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Good（2.0スタイル）
async def get_active_tasks(session: AsyncSession) -> list[Task]:
    result = await session.execute(
        select(Task).where(Task.completed == False).order_by(Task.created_at)
    )
    return list(result.scalars().all())

# Bad（レガシーQuery API）
def get_active_tasks(session: Session) -> list[Task]:
    return session.query(Task).filter(Task.completed == False).all()
```

## テスト

### テストファイルの配置

```
tests/
├── conftest.py              # 共通fixture（TestClient）
├── unit/                    # ユニットテスト
│   ├── conftest.py
│   └── test_crud.py         # CRUD関数のテスト
└── integration/             # インテグレーションテスト
    ├── conftest.py
    └── test_tasks_api.py    # エンドポイントのテスト
```

### FastAPI のテスト

`TestClient` を使用してエンドポイントをテストすること。

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_task():
    """タスク作成エンドポイントのテスト。"""
    response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "Test Description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data
```

### 非同期テスト

非同期関数のテストには `@pytest.mark.asyncio` を使用（ただし `asyncio_mode = "auto"` 設定により自動適用）。

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

async def test_get_task(session: AsyncSession):
    """タスク取得のテスト。"""
    task = await crud.create_task(session, TaskCreate(title="Test"))
    result = await crud.get_task(session, task.id)
    assert result is not None
    assert result.title == "Test"
```

## コードスタイル

### Ruff設定

プロジェクトのRuff設定に従うこと（自動適用）。

- 行の長さ: 最大100文字
- インポート順序: 標準ライブラリ → サードパーティ → ファーストパーティ
- 自動フォーマット: `uv task fmt`

### 命名規則

- 変数・関数: `snake_case`
- クラス: `PascalCase`
- 定数: `UPPER_SNAKE_CASE`
- プライベート: `_leading_underscore`

```python
# Good
class UserManager:
    MAX_LOGIN_ATTEMPTS = 5

    def __init__(self):
        self._cache: dict[int, User] = {}

    async def get_user(self, user_id: int) -> User | None:
        return self._cache.get(user_id)
```

## 禁止事項

### 避けるべきパターン

- 型ヒントなしのコード
- 同期的なブロッキング処理（ファイルI/O、DB操作）
- レガシーなSQLAlchemy Query API
- `print()` デバッグ（本番コードに残さない）
- 古い型記法（`List`, `Dict`, `Optional`）

### セキュリティ

以下の脆弱性に注意すること：

- **SQLインジェクション**: SQLAlchemyのORMを使用（生SQLは避ける）
- **XSS**: Pydanticでバリデーション、FastAPIが自動エスケープ
- **機密情報**: 環境変数で管理、ハードコーディング禁止

```python
# Good（パラメータ化されたクエリ）
result = await session.execute(
    select(User).where(User.email == email)
)

# Bad（SQLインジェクションの危険）
result = await session.execute(
    f"SELECT * FROM users WHERE email = '{email}'"
)
```

## 開発ツール

### コマンド

```bash
uv task fmt          # Ruffで自動フォーマット
uv task lint         # Ruffでリント（自動修正）
uv task type         # mypyで型チェック
uv task test         # pytest実行
uv task check        # すべてのチェック実行
```

### pre-commit

コミット前に自動チェックが実行されます（`.pre-commit-config.yaml`）。

## まとめ

- Python 3.13の機能を活用
- すべてに型ヒントを付ける
- 非同期処理を優先
- FastAPIの標準的な構造に従う
- SQLAlchemy 2.0+の新記法を使用
- セキュリティを常に意識
