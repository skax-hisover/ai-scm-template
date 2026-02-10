"""
샘플 Celery 태스크.

새로운 비동기 태스크를 추가할 때 이 파일을 참고하세요.

사용 예 (API에서 호출):
    from app.tasks.sample_tasks import send_welcome_email
    send_welcome_email.delay(user_id=str(user.id), email=user.email)
"""

import time

from app.core.logging import get_logger
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id: str, email: str) -> dict:
    """
    환영 이메일 발송 태스크 (샘플).

    Args:
        user_id: 사용자 ID
        email: 수신자 이메일

    Returns:
        처리 결과
    """
    try:
        logger.info(
            "환영 이메일 발송 시작",
            extra={"user_id": user_id, "email": email},
        )
        # TODO: 실제 이메일 발송 로직 구현
        time.sleep(1)  # 이메일 발송 시뮬레이션

        logger.info(
            "환영 이메일 발송 완료",
            extra={"user_id": user_id, "email": email},
        )
        return {"status": "success", "email": email}
    except Exception as exc:
        logger.error(
            "환영 이메일 발송 실패",
            extra={"user_id": user_id, "email": email, "error": str(exc)},
        )
        # 재시도
        raise self.retry(exc=exc)


@celery_app.task
def sample_periodic_task() -> dict:
    """
    주기적 실행 태스크 (샘플).

    celery beat 스케줄러에 등록하여 주기적으로 실행할 수 있습니다.
    """
    logger.info("주기적 태스크 실행")
    # TODO: 실제 주기적 작업 로직 구현
    return {"status": "completed"}
