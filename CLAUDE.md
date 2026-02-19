# CLAUDE.md

## 詳細ガイドライン

| トピック | ファイル |
|--------|--------|
| Python・非同期処理・SQLAlchemy・FastAPI構成 | `.github/instructions/python.instructions.md` |
| Docker・Docker Compose・DevContainer | `.github/instructions/docker.instructions.md` |
| Gitワークフロー・CI/CD・コミット規約・PR | `.github/instructions/general.instructions.md` |
| 開発哲学・アーキテクチャ全体 | `.github/copilot-instructions.md` |

## 主要コマンド

```bash
uv task fmt          # Ruff で自動フォーマット（ファイル変更あり）
uv task fmt-check    # フォーマットチェックのみ
uv task lint         # Ruff Lint（自動修正あり）
uv task lint-check   # Lint チェックのみ
uv task type         # mypy 型チェック（strict）
uv task test         # pytest（カバレッジ付き）
uv task test-unit    # ユニットテストのみ
uv task test-integration  # 統合テストのみ
uv task check        # 全チェック一括（PR 前に必須）
```

## プロジェクト構造

```
app/
├── main.py          # エントリーポイント・lifespan 管理
├── core/            # インフラ（ロギング・設定）
├── routers/         # HTTPリクエスト/レスポンス処理のみ
├── schemas/         # Pydantic入出力モデル
├── crud/            # ビジネスロジック・DBアクセス
└── models/          # SQLAlchemy モデル定義
tests/
├── conftest.py      # 共通フィクスチャ
├── unit/            # ユニットテスト
└── integration/     # 統合テスト（APIエンドポイント）
alembic/             # DBマイグレーションスクリプト
```

## 重要制約

1. **非同期必須**: 全 I/O（DB・HTTP・ファイル）に `async`/`await` と `AsyncSession` を使用
2. **型安全**: 全関数に型ヒント必須。`mypy` strict を通すこと
3. **レイヤー分離**: ルーターにビジネスロジックを書かない。CRUD に HTTP ロジックを書かない
4. **日本語 docstring**: 全関数・クラスのdocstringは日本語で記述
5. **最小変更**: 要求された変更のみ行う。不要なリファクタリングは禁止

## コミットメッセージ規約

```
<type>: <概要>

<本文（任意）>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

type: `feat` / `fix` / `docs` / `style` / `refactor` / `test` / `chore` / `perf`

## ブランチ戦略

- `feature/add-ci` — メインブランチ（PRのベース）
- `feature/*` — 新機能
- `fix/*` — バグ修正
- `chore/*` — 設定・雑務
