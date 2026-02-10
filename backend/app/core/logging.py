"""
구조화된 로깅 설정 모듈.

JSON 형식의 구조화된 로그를 출력합니다.
운영 환경에서는 ELK, CloudWatch 등의 로그 수집기와 연동할 수 있습니다.

[개발 표준]
- print() 대신 반드시 logger를 사용하세요.
- 각 모듈에서: from app.core.logging import get_logger; logger = get_logger(__name__)
- 로그 레벨 가이드:
    - DEBUG: 개발 디버깅용 상세 정보
    - INFO: 정상 동작 확인 (API 호출, 작업 완료 등)
    - WARNING: 비정상이지만 처리 가능한 상황
    - ERROR: 오류 발생 (예외 처리됨)
    - CRITICAL: 시스템 중단 수준의 심각한 오류
"""

import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from app.core.config import settings


def setup_logging() -> None:
    """애플리케이션 로깅을 초기화합니다."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # JSON 포맷터 설정
    formatter = JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger",
        },
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # SQLAlchemy 로거 레벨 조정 (너무 많은 로그 방지)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # uvicorn 로거
    logging.getLogger("uvicorn.access").setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """
    모듈별 로거를 반환합니다.

    사용 예:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("작업 완료", extra={"user_id": "123", "action": "create_item"})

    Args:
        name: 로거 이름 (일반적으로 __name__)

    Returns:
        logging.Logger 인스턴스
    """
    return logging.getLogger(name)
