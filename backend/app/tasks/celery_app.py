"""
Celery 애플리케이션 설정.

사용법:
    # 워커 실행
    celery -A app.tasks.celery_app worker --loglevel=info

    # 비트 스케줄러 실행 (주기적 태스크용)
    celery -A app.tasks.celery_app beat --loglevel=info

    # 워커 + 비트 동시 실행 (개발용)
    celery -A app.tasks.celery_app worker --beat --loglevel=info
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "ai_scm",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery 설정
celery_app.conf.update(
    # 직렬화 형식
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # 시간대
    timezone="Asia/Seoul",
    enable_utc=True,
    # 태스크 결과 만료 시간 (1일)
    result_expires=86400,
    # 워커 동시 처리 수
    worker_concurrency=4,
    # 태스크 자동 검색
    task_routes={
        "app.tasks.agent_tasks.*": {"queue": "default"},
        "app.tasks.sample_tasks.*": {"queue": "default"},
        # "app.tasks.email_tasks.*": {"queue": "email"},
        # "app.tasks.report_tasks.*": {"queue": "report"},
    },
)

# 태스크 모듈 자동 검색
celery_app.autodiscover_tasks(["app.tasks"])
