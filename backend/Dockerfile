# ============================================================================
# AI-SCM Backend Dockerfile
# ============================================================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 의존성 설치 (캐시 레이어 최적화)
COPY backend/pyproject.toml backend/uv.lock* /app/backend/
RUN cd backend && uv sync --frozen --no-install-workspace 2>/dev/null || \
    (uv pip compile pyproject.toml -o requirements.txt && uv pip install --system -r requirements.txt)

# 소스 복사
COPY backend/ /app/backend/

WORKDIR /app/backend

# 포트 노출
EXPOSE 8000

# 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
