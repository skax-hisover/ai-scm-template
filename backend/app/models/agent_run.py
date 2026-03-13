"""
Agent 실행 이력 ORM 모델.

[개발 표준]
- 외부 Agent 플랫폼 호출 이력/상태를 저장합니다.
- 실행 상태는 queued/running/succeeded/failed 중 하나를 사용합니다.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AgentRun(TimestampMixin, Base):
    """Agent 실행 이력 테이블."""

    __tablename__ = "agent_runs"

    agent_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True, comment="Agent 식별자")
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True, comment="실행 상태")
    input_text: Mapped[str] = mapped_column(Text, nullable=False, comment="입력 프롬프트/요청")
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Agent 응답 결과")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="실패 시 에러 메시지")
    external_run_id: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="외부 플랫폼 실행 ID")
    model_name: Mapped[str | None] = mapped_column(String(120), nullable=True, comment="요청 모델명")
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True, comment="추가 메타데이터(JSON 문자열)")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="실행 시작 시각")
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="실행 종료 시각"
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="요청 사용자 ID",
    )

    owner: Mapped["User"] = relationship("User")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        return f"<AgentRun(id={self.id}, agent_id={self.agent_id}, status={self.status})>"

