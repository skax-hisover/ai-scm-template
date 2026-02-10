"""
아이템 관련 스키마 (샘플).

[개발 표준]
- 새로운 비즈니스 엔티티의 스키마를 추가할 때 이 파일을 참고하세요.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """아이템 생성 요청."""

    title: str = Field(..., min_length=1, max_length=255, examples=["새로운 아이템"])
    description: str | None = Field(None, max_length=1000, examples=["아이템 설명입니다"])


class ItemUpdate(BaseModel):
    """아이템 수정 요청 (부분 업데이트)."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class ItemResponse(BaseModel):
    """아이템 응답."""

    id: uuid.UUID
    title: str
    description: str | None = None
    owner_id: uuid.UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    """아이템 목록 응답."""

    data: list[ItemResponse]
    total: int
