"""
전역 에러 핸들러.

예상치 못한 예외를 잡아서 일관된 에러 응답을 반환합니다.

[개발 표준]
- 비즈니스 로직 에러는 HTTPException을 사용하세요.
- 이 핸들러는 예상치 못한 서버 에러(500)만 처리합니다.
- 프로덕션에서는 에러 상세 내용을 클라이언트에 노출하지 않습니다.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """FastAPI 앱에 에러 핸들러를 등록합니다."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """요청 유효성 검증 에러 핸들러."""
        logger.warning(
            "요청 유효성 검증 실패",
            extra={
                "path": request.url.path,
                "errors": str(exc.errors()),
            },
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "요청 데이터가 유효하지 않습니다",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """전역 예외 핸들러 (500 Internal Server Error)."""
        logger.error(
            "처리되지 않은 예외 발생",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            exc_info=True,
        )

        # 로컬 환경에서는 상세 에러 메시지 반환
        detail = str(exc) if settings.ENVIRONMENT == "local" else "서버 내부 오류가 발생했습니다"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": detail},
        )
