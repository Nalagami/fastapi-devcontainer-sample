# --- 共通ステージ ---
FROM python:3.13-bookworm AS base
WORKDIR /app

# .pycファイルを生成しない、標準出力をバッファリングしない
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- 開発環境用 ---
FROM base AS development
WORKDIR /workspace

ENV PATH="/workspace/.venv/bin:$PATH"

# 日本語ロケールを設定
RUN apt-get update && apt-get install -y locales \
    && sed -i '/ja_JP.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=ja_JP.UTF-8
RUN echo "ja_JP.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8

RUN pip install --no-cache-dir uv
COPY ../pyproject.toml .
RUN uv sync --extra dev

# --- 本番環境用 ---
FROM base AS production
WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

RUN pip install --no-cache-dir uv
COPY ../pyproject.toml .
RUN uv sync
# TODO: なぜかDockerfileと__pycache__がコピーされてしまうのを解消する
COPY ./app/ /app

# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "main:app"]
