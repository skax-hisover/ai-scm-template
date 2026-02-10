"""
날짜/시간 유틸리티.

[개발 표준]
- 모든 날짜/시간은 UTC 기준으로 저장합니다.
- 프론트엔드에 전달 시 ISO 8601 형식을 사용합니다.
- 사용자 표시용 변환은 프론트엔드에서 수행합니다.
"""

from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """현재 UTC 시간을 반환합니다."""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime | None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """datetime을 문자열로 포맷팅합니다."""
    if dt is None:
        return ""
    return dt.strftime(fmt)


def format_date(dt: datetime | None, fmt: str = "%Y-%m-%d") -> str:
    """datetime에서 날짜만 문자열로 포맷팅합니다."""
    if dt is None:
        return ""
    return dt.strftime(fmt)
