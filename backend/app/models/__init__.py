"""
SQLAlchemy ORM 모델 패키지.

[개발 표준]
- 새로운 모델 추가 시 이 파일에 import를 추가하세요 (Alembic 자동감지용).
- 모든 모델은 Base를 상속받아야 합니다.
- 테이블명은 snake_case 복수형을 사용합니다 (예: users, items).
- id는 UUID를 기본으로 사용합니다.
- 생성일/수정일 컬럼은 TimestampMixin을 사용하세요.
"""

from app.models.agent_run import AgentRun  # noqa: F401
from app.models.base import Base, TimestampMixin  # noqa: F401
from app.models.item import Item  # noqa: F401
from app.models.user import User  # noqa: F401
