"""
요청/응답 로깅 미들웨어.

모든 HTTP 요청과 응답을 구조화된 형식으로 로깅합니다.

[개발 표준]
- 민감한 정보 (Authorization 헤더, 비밀번호 등)는 로그에 포함하지 마세요.
- 헬스체크 엔드포인트는 로그에서 제외합니다 (로그 노이즈 방지).
"""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)

# 로그에서 제외할 경로
EXCLUDE_PATHS = {"/api/v1/health", "/docs", "/redoc", "/openapi.json"}


class LoggingMiddleware(BaseHTTPMiddleware):
    """HTTP 요청/응답 로깅 미들웨어."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 제외 경로 스킵
        if request.url.path in EXCLUDE_PATHS:
            return await call_next(request)

        # 요청 ID 생성 (추적용)
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        # 요청 로그
        logger.info(
            "요청 시작",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
                "query_params": str(request.query_params),
            },
        )

        # 요청 처리
        response = await call_next(request)

        # 응답 로그
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(
            "요청 완료",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        # 응답 헤더에 요청 ID 추가 (프론트엔드 디버깅용)
        response.headers["X-Request-ID"] = request_id

        return response
