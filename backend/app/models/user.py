"""
사용자(User) ORM 모델.

[개발 표준]
- 비밀번호는 hashed_password로만 저장합니다 (평문 저장 금지).
- 이메일은 unique 제약을 걸어야 합니다.
- 삭제는 is_active=False (소프트 삭제)를 권장합니다.
"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    """사용자 테이블."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False, comment="이메일"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="해시된 비밀번호"
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="이름"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="활성 상태"
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="관리자 여부"
    )

    # Relationships
    items: Mapped[list["Item"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Item", back_populates="owner", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
