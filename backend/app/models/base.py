"""
SQLAlchemy Base 모델 및 공통 Mixin.

[개발 표준]
- 모든 ORM 모델은 Base를 상속받습니다.
- created_at, updated_at이 필요한 모델은 TimestampMixin을 함께 상속합니다.
- 예: class Item(TimestampMixin, Base): ...
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """모든 ORM 모델의 Base 클래스."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="PK (UUID)",
    )


class TimestampMixin:
    """생성일/수정일 자동 관리 Mixin."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
        comment="생성일시",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
        comment="수정일시",
    )
