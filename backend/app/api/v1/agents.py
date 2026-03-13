"""
Agent 실행 API.
"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, DbSession
from app.crud import agent_run_crud
from app.schemas.agent import AgentRunCreate, AgentRunListResponse, AgentRunResponse
from app.services.agent_client import invoke_agent_run
from app.tasks.agent_tasks import process_agent_run

router = APIRouter()


@router.post("/runs", response_model=AgentRunResponse, status_code=201)
def create_agent_run(
    db: DbSession,
    current_user: CurrentUser,
    run_in: AgentRunCreate,
) -> Any:
    """Agent 실행 요청을 생성합니다."""
    run = agent_run_crud.create_run(db, owner_id=current_user.id, run_in=run_in)

    if run_in.sync:
        try:
            result = invoke_agent_run(
                agent_id=run_in.agent_id,
                input_text=run_in.input_text,
                model_name=run_in.model_name,
                metadata=run_in.metadata,
            )
            run = agent_run_crud.mark_succeeded(
                db,
                db_obj=run,
                output_text=result["output_text"],
                external_run_id=result.get("external_run_id"),
                metadata_update=result.get("raw_response"),
            )
        except Exception as exc:
            run = agent_run_crud.mark_failed(db, db_obj=run, error_message=str(exc))
        return run

    try:
        process_agent_run.delay(str(run.id))
    except Exception as exc:
        run = agent_run_crud.mark_failed(
            db,
            db_obj=run,
            error_message=f"큐 등록 실패: {str(exc)}",
        )
    return run


@router.get("/runs", response_model=AgentRunListResponse)
def list_agent_runs(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """Agent 실행 이력 목록을 조회합니다."""
    runs = agent_run_crud.list_for_user(
        db,
        owner_id=current_user.id,
        is_superuser=current_user.is_superuser,
        skip=skip,
        limit=limit,
    )
    total = agent_run_crud.count_for_user(db, owner_id=current_user.id, is_superuser=current_user.is_superuser)
    return AgentRunListResponse(data=runs, total=total)


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
def get_agent_run(
    db: DbSession,
    current_user: CurrentUser,
    run_id: uuid.UUID,
) -> Any:
    """Agent 실행 이력 단건을 조회합니다."""
    run = agent_run_crud.get_for_user(
        db,
        run_id=run_id,
        owner_id=current_user.id,
        is_superuser=current_user.is_superuser,
    )
    if not run:
        raise HTTPException(status_code=404, detail="실행 이력을 찾을 수 없습니다")
    return run
