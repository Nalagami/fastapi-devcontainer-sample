# GitHub Copilot Instructions

## プロジェクト概要

Python 3.13とFastAPIを使用したWebアプリケーションです。SQLAlchemyとAlembicを使用したデータベース管理、型安全性を重視した開発を行っています。

## 技術スタック

- **言語**: Python 3.13
- **Webフレームワーク**: FastAPI
- **ORM**: SQLAlchemy 2.0+ (async)
- **マイグレーション**: Alembic
- **パッケージ管理**: uv
- **Linter/Formatter**: Ruff
- **型チェック**: mypy
- **テスト**: pytest (pytest-asyncio, pytest-cov)

## プロジェクト構造

```
app/
├── main.py         # FastAPIアプリケーションのエントリーポイント
├── models/         # SQLAlchemyモデル（データベーステーブル定義）
├── schemas/        # Pydanticスキーマ（リクエスト/レスポンス型）
├── crud/           # CRUD操作（データベース操作ロジック）
└── routers/        # FastAPIルーター（エンドポイント定義）
```

## コーディング規約

### 型ヒント

- **必須**: すべての関数・メソッドに型ヒントを付けること
- 引数、戻り値、変数には明示的に型を指定する
- Python 3.13のモダンな型記法を使用（`list[str]`、`dict[str, int]`など）

```python
# Good
async def get_task(task_id: int) -> Task | None:
    """タスクをIDで取得する。"""
    return await db.get(Task, task_id)

# Bad（型ヒントがない）
async def get_task(task_id):
    return await db.get(Task, task_id)
```

### 非同期処理

- FastAPIのエンドポイントとデータベース操作には `async/await` を使用
- I/O操作は可能な限り非同期で実装する
- SQLAlchemyは AsyncSession を使用

```python
# Good
@app.get("/tasks/{task_id}")
async def read_task(task_id: int, session: AsyncSession = Depends(get_session)) -> Task:
    return await crud.get_task(session, task_id)

# Bad（同期処理）
@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    return crud.get_task(task_id)
```

### Docstring

- すべての関数・クラスに日本語のdocstringを記述
- 1行の簡潔な説明で十分（詳細な説明が必要な場合のみ複数行）

```python
def calculate_total(items: list[int]) -> int:
    """アイテムの合計を計算する。"""
    return sum(items)
```

### インポート順序

Ruffの設定により自動的に整理されます：
1. 標準ライブラリ
2. サードパーティライブラリ
3. ファーストパーティ（app）

### コードスタイル

- 行の長さ: 最大100文字（Ruff設定）
- Ruffによる自動フォーマットに従う
- `uv task fmt` でフォーマット実行

## ベストプラクティス

### FastAPI

- ルーター（routers/）でエンドポイントを定義
- ビジネスロジックはCRUD層（crud/）に実装
- リクエスト/レスポンスの型はPydanticスキーマ（schemas/）で定義
- データベースモデルはmodels/に配置

### データベース

- モデル定義には `DeclarativeBase` を継承したベースクラスを使用
- マイグレーションはAlembicで管理（`alembic revision --autogenerate`）
- 本番環境では自動マイグレーション（起動時の`upgrade head`）を実行

### エラーハンドリング

- FastAPIの `HTTPException` を使用
- 適切なステータスコードを返す（404, 400, 500など）

```python
from fastapi import HTTPException

if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

### テスト

- `tests/unit/`: ユニットテスト（個別の関数・クラス）
- `tests/integration/`: インテグレーションテスト（エンドポイント）
- FastAPIの `TestClient` を使用してエンドポイントをテスト
- 非同期テストには `@pytest.mark.asyncio` を使用（`asyncio_mode = "auto"`設定済み）

## 禁止事項

- 型ヒントなしのコードを書かないこと（mypy strict設定）
- FastAPIエンドポイントでのデフォルト引数での関数呼び出し（B008）は許可（FastAPIの標準パターン）
- `print()`デバッグは本番コードに残さない（開発時のみ使用）
- 同期的なブロッキング処理（ファイルI/O、HTTPリクエスト）は避ける

## タスク実行コマンド

開発時に使用する主なコマンド：

```bash
uv task fmt          # コード自動フォーマット
uv task lint         # リント実行（自動修正）
uv task type         # 型チェック
uv task test         # テスト実行
uv task check        # すべてのチェック実行
```

## その他

- DevContainer環境での開発を推奨
- Python 3.13の新機能を積極的に活用
- セキュリティを考慮したコード（SQLインジェクション、XSSなど）
