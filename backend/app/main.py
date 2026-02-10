"""
FastAPI 애플리케이션 엔트리포인트.

[실행 방법]
    # 개발 (자동 리로드)
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

    # 또는 FastAPI CLI
    fastapi run --reload app/main.py
"""

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.error_handler import register_error_handlers
from app.middleware.logging_middleware import LoggingMiddleware


def custom_generate_unique_id(route: APIRoute) -> str:
    """OpenAPI operationId를 tag-name 형식으로 생성합니다."""
    return f"{route.tags[0]}-{route.name}"


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 팩토리."""

    # 로깅 초기화
    setup_logging()

    # Sentry 초기화 (프로덕션)
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
        sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

    # FastAPI 앱 생성
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AI-SCM Template API",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        generate_unique_id_function=custom_generate_unique_id,
    )

    # ─── CORS 설정 ───────────────────────────────────────────
    if settings.all_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # ─── 미들웨어 등록 ──────────────────────────────────────
    app.add_middleware(LoggingMiddleware)

    # ─── 에러 핸들러 등록 ────────────────────────────────────
    register_error_handlers(app)

    # ─── API 라우터 등록 ─────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


# 애플리케이션 인스턴스
app = create_app()
