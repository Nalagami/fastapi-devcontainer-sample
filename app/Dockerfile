# --- 共通ステージ ---
FROM python:3.13-bookworm AS base

# .pycファイルを生成しない、標準出力をバッファリングしない
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- 開発環境用 ---
FROM base AS development
WORKDIR /workspace

# 日本語ロケールを設定
RUN apt-get update && apt-get install -y locales \
    && sed -i '/ja_JP.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=ja_JP.UTF-8
RUN echo "ja_JP.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8

RUN useradd -m -s /bin/bash vscode \
    && chown vscode:vscode /workspace
USER vscode

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ../pyproject.toml .
RUN uv sync --group dev

# --- 本番環境用 ---
FROM base AS production
WORKDIR /workspace

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ../pyproject.toml .
RUN uv sync
# TODO: なぜかDockerfileと__pycache__がコピーされてしまうのを解消する
COPY ./app/ .

# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "app.main:app"]
