"""
초기 데이터 생성 스크립트.

최초 실행 시 슈퍼유저 계정을 생성합니다.

[사용법]
    python -m app.initial_data
"""

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import get_logger, setup_logging
from app.crud import user_crud
from app.schemas.user import UserCreate

logger = get_logger(__name__)


def init_db() -> None:
    """초기 데이터를 생성합니다."""
    db = SessionLocal()
    try:
        # 슈퍼유저 존재 여부 확인
        user = user_crud.get_by_email(db, email=settings.FIRST_SUPERUSER)
        if not user:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                full_name="System Admin",
            )
            user_crud.create(db, obj_in=user_in)
            logger.info(
                "슈퍼유저 생성 완료",
                extra={"email": settings.FIRST_SUPERUSER},
            )
        else:
            logger.info("슈퍼유저가 이미 존재합니다")
    finally:
        db.close()


if __name__ == "__main__":
    setup_logging()
    logger.info("초기 데이터 생성 시작")
    init_db()
    logger.info("초기 데이터 생성 완료")
