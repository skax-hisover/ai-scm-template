"""
아이템(Item) ORM 모델 - 샘플 비즈니스 엔티티.

[개발 표준]
- 새로운 비즈니스 엔티티를 추가할 때 이 파일을 참고 템플릿으로 사용하세요.
- 외래키는 명시적으로 ondelete 옵션을 지정하세요.
- relationship은 양방향으로 정의하세요 (back_populates 사용).
"""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Item(TimestampMixin, Base):
    """아이템 테이블 (샘플 비즈니스 엔티티)."""

    __tablename__ = "items"

    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="제목")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="설명")
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="소유자 ID",
    )

    # Relationships
    owner: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="items"
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, title={self.title})>"
