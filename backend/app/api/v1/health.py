"""
헬스체크 API.

로드밸런서, 모니터링 도구에서 서비스 상태를 확인하는 용도입니다.

[개발 표준]
- /health: 단순 생존 확인 (로드밸런서용, 인증 불필요)
- /health/detailed: DB 등 구성요소별 상태 확인 (대시보드용, 인증 불필요)
"""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal
from app.schemas.common import Message

router = APIRouter()


@router.get("/health", response_model=Message)
def health_check() -> Message:
    """서비스 헬스체크."""
    return Message(message="OK")


@router.get("/health/detailed")
def detailed_health_check() -> dict:
    """
    상세 시스템 상태 체크.

    DB 연결 등 주요 구성요소의 상태를 확인하여
    대시보드에서 시스템 상태를 동적으로 표시하는 용도입니다.
    """
    checks: dict[str, dict] = {}
    overall = "정상"

    # 1. DB 연결 체크
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            checks["database"] = {"status": "정상", "message": "DB 연결 정상"}
        finally:
            db.close()
    except Exception as e:
        checks["database"] = {"status": "오류", "message": f"DB 연결 실패: {str(e)}"}
        overall = "오류"

    # 2. Redis 연결 체크 (Celery 브로커)
    try:
        import redis

        from app.core.config import settings

        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_connect_timeout=2,
        )
        r.ping()
        checks["redis"] = {"status": "정상", "message": "Redis 연결 정상"}
        r.close()
    except Exception:
        checks["redis"] = {"status": "경고", "message": "Redis 미연결 (선택 구성요소)"}
        # Redis는 선택 사항이므로 overall을 "오류"로 변경하지 않고 "경고"로만 표시
        if overall == "정상":
            overall = "경고"

    return {
        "overall": overall,
        "checks": checks,
    }
