"""
Alembic 환경 설정.

모델 변경 감지 및 마이그레이션 스크립트를 자동 생성합니다.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Alembic Config 객체
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 모든 모델을 import하여 MetaData에 등록
from app.models import Base  # noqa: E402
from app.core.config import settings  # noqa: E402

# Alembic이 추적할 MetaData
target_metadata = Base.metadata


def get_url() -> str:
    """데이터베이스 URL을 반환합니다."""
    return settings.database_url


def run_migrations_offline() -> None:
    """오프라인 모드에서 마이그레이션을 실행합니다."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인 모드에서 마이그레이션을 실행합니다."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
