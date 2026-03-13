"""
Agent 실행 이력 CRUD.
"""

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.agent_run import AgentRun
from app.schemas.agent import AgentRunCreate


class CRUDAgentRun(CRUDBase[AgentRun, AgentRunCreate, AgentRunCreate]):
    """Agent 실행 이력 전용 CRUD."""

    def create_run(self, db: Session, *, owner_id: uuid.UUID, run_in: AgentRunCreate) -> AgentRun:
        """실행 이력 레코드를 생성합니다."""
        metadata_json = json.dumps(run_in.metadata, ensure_ascii=False) if run_in.metadata else None
        status = "running" if run_in.sync else "queued"
        started_at = datetime.now(UTC) if run_in.sync else None

        db_obj = AgentRun(
            agent_id=run_in.agent_id,
            status=status,
            input_text=run_in.input_text,
            owner_id=owner_id,
            model_name=run_in.model_name,
            metadata_json=metadata_json,
            started_at=started_at,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_for_user(self, db: Session, *, run_id: uuid.UUID, owner_id: uuid.UUID, is_superuser: bool) -> AgentRun | None:
        """권한을 고려해 단건 실행 이력을 조회합니다."""
        stmt = select(AgentRun).where(AgentRun.id == run_id)
        if not is_superuser:
            stmt = stmt.where(AgentRun.owner_id == owner_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def list_for_user(
        self,
        db: Session,
        *,
        owner_id: uuid.UUID,
        is_superuser: bool,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AgentRun]:
        """권한을 고려해 실행 이력 목록을 조회합니다."""
        stmt = select(AgentRun)
        if not is_superuser:
            stmt = stmt.where(AgentRun.owner_id == owner_id)
        stmt = stmt.order_by(desc(AgentRun.created_at)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return list(result.scalars().all())

    def count_for_user(self, db: Session, *, owner_id: uuid.UUID, is_superuser: bool) -> int:
        """권한을 고려해 실행 이력 건수를 조회합니다."""
        stmt = select(func.count()).select_from(AgentRun)
        if not is_superuser:
            stmt = stmt.where(AgentRun.owner_id == owner_id)
        result = db.execute(stmt)
        return result.scalar_one()

    def mark_running(self, db: Session, *, db_obj: AgentRun) -> AgentRun:
        """상태를 running으로 전환합니다."""
        db_obj.status = "running"
        db_obj.started_at = datetime.now(UTC)
        db_obj.error_message = None
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def mark_succeeded(
        self,
        db: Session,
        *,
        db_obj: AgentRun,
        output_text: str,
        external_run_id: str | None = None,
        metadata_update: dict[str, Any] | None = None,
    ) -> AgentRun:
        """상태를 succeeded로 전환합니다."""
        db_obj.status = "succeeded"
        db_obj.output_text = output_text
        db_obj.external_run_id = external_run_id
        db_obj.finished_at = datetime.now(UTC)
        if metadata_update is not None:
            db_obj.metadata_json = json.dumps(metadata_update, ensure_ascii=False)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def mark_failed(self, db: Session, *, db_obj: AgentRun, error_message: str) -> AgentRun:
        """상태를 failed로 전환합니다."""
        db_obj.status = "failed"
        db_obj.error_message = error_message
        db_obj.finished_at = datetime.now(UTC)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


agent_run_crud = CRUDAgentRun(AgentRun)

