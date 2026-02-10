"""
헬스체크 API.

로드밸런서, 모니터링 도구에서 서비스 상태를 확인하는 용도입니다.
"""

from fastapi import APIRouter

from app.schemas.common import Message

router = APIRouter()


@router.get("/health", response_model=Message)
def health_check() -> Message:
    """서비스 헬스체크."""
    return Message(message="OK")
