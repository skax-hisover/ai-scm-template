"""
Agent 실행 비동기 태스크.
"""

import json
import uuid
from typing import Any

from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.crud.agent_run import agent_run_crud
from app.services.agent_client import invoke_agent_run
from app.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def process_agent_run(self, run_id: str) -> dict[str, Any]:
    """Agent 실행 이력을 큐에서 처리합니다."""
    db = SessionLocal()
    try:
        run_uuid = uuid.UUID(run_id)
        run = agent_run_crud.get(db, id=run_uuid)
        if not run:
            logger.warning("AgentRun not found", extra={"run_id": run_id})
            return {"status": "not_found", "run_id": run_id}

        agent_run_crud.mark_running(db, db_obj=run)
        result = invoke_agent_run(
            agent_id=run.agent_id,
            input_text=run.input_text,
            model_name=run.model_name,
            metadata=json.loads(run.metadata_json) if run.metadata_json else None,
        )
        agent_run_crud.mark_succeeded(
            db,
            db_obj=run,
            output_text=result["output_text"],
            external_run_id=result.get("external_run_id"),
            metadata_update=result.get("raw_response"),
        )
        return {"status": "succeeded", "run_id": run_id}
    except Exception as exc:
        run = agent_run_crud.get(db, id=uuid.UUID(run_id))
        if run:
            agent_run_crud.mark_failed(db, db_obj=run, error_message=str(exc))
        logger.error("Agent run task failed", extra={"run_id": run_id, "error": str(exc)})
        raise self.retry(exc=exc) from exc
    finally:
        db.close()

