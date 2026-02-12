"""
데이터베이스 연결 및 세션 관리 모듈.

SQLAlchemy를 사용하여 PostgreSQL에 연결합니다.

[개발 표준]
- 모든 DB 작업은 SessionLocal 또는 get_db() 의존성을 통해 수행합니다.
- 직접 engine을 사용하지 마세요. 세션을 통해 작업하세요.
- 트랜잭션은 서비스 레이어 또는 API 레이어에서 commit/rollback을 관리합니다.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Engine 생성
# - pool_pre_ping: 연결 유효성을 사전 확인하여 끊어진 연결 방지
# - pool_size: 커넥션 풀 기본 크기
# - max_overflow: 풀 초과 시 추가로 생성할 수 있는 최대 연결 수
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.ENVIRONMENT == "local",  # 로컬에서만 SQL 로그 출력
)

# 세션 팩토리
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI Dependency Injection용 DB 세션 생성기.

    사용 예:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
