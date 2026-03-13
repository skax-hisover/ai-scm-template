"""
Agent 실행 관련 스키마.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentRunCreate(BaseModel):
    """Agent 실행 생성 요청."""

    agent_id: str = Field(..., min_length=1, max_length=120, examples=["default-agent"])
    input_text: str = Field(..., min_length=1, examples=["오늘 주요 이슈 요약해줘"])
    sync: bool = Field(False, description="true면 동기 실행, false면 Celery 큐 실행")
    model_name: str | None = Field(None, max_length=120, examples=["gpt-4.1-mini"])
    metadata: dict[str, Any] | None = Field(None, description="추가 메타데이터")


class AgentRunResponse(BaseModel):
    """Agent 실행 응답."""

    id: uuid.UUID
    agent_id: str
    status: str
    input_text: str
    output_text: str | None = None
    error_message: str | None = None
    external_run_id: str | None = None
    model_name: str | None = None
    metadata_json: str | None = None
    owner_id: uuid.UUID
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AgentRunListResponse(BaseModel):
    """Agent 실행 목록 응답."""

    data: list[AgentRunResponse]
    total: int
