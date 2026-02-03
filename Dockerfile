# ============================================================================
# Stage 1: Development (開発用)
# DevContainer と開発時のコンテナ実行に使用
# ============================================================================
FROM python:3.13-slim AS development

ARG TERRAFORM_VERSION=1.7.0

WORKDIR /workspace

# 開発ツールをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Terraform をインストール
RUN wget -q https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    terraform version

# uv をインストール
RUN pip install --no-cache-dir uv

# 依存関係をインストール
COPY pyproject.toml .
RUN uv sync --all-extras

ENV PATH="/workspace/.venv/bin:$PATH"
ENV VIRTUAL_ENV=/workspace/.venv

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# ============================================================================
# Stage 2: Production (本番用)
# 最小化されたプロダクション向けイメージ
# ============================================================================
FROM python:3.13-slim AS production

WORKDIR /app

# 運用に最小限なパッケージのみ
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 開発ステージから本番に必要なパッケージのみをコピー
COPY --from=development /workspace/.venv /app/.venv

# アプリケーションコードをコピー
COPY main.py .

ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV=/app/.venv
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
