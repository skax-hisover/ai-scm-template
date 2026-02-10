"""
사용자 관련 스키마.

[개발 표준]
- password 필드는 응답 스키마에 절대 포함하지 마세요.
- 이메일 유효성 검증은 EmailStr을 사용합니다.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """사용자 생성 요청."""

    email: EmailStr = Field(..., max_length=255, examples=["user@example.com"])
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = Field(None, max_length=255, examples=["홍길동"])
    is_active: bool = True
    is_superuser: bool = False


class UserUpdate(BaseModel):
    """사용자 수정 요청 (부분 업데이트)."""

    email: EmailStr | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=128)
    full_name: str | None = Field(None, max_length=255)
    is_active: bool | None = None


class UserResponse(BaseModel):
    """사용자 응답 (비밀번호 제외)."""

    id: uuid.UUID
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    is_superuser: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """사용자 목록 응답."""

    data: list[UserResponse]
    total: int
