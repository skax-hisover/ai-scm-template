"""
사용자 관리 API.

[개발 표준]
- 사용자 목록 조회는 관리자만 가능합니다.
- 비밀번호는 응답에 포함하지 마세요 (UserResponse 스키마 사용).
"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentSuperUser, DbSession
from app.crud import user_crud
from app.schemas.common import Message
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=UserListResponse)
def list_users(
    db: DbSession,
    _current_user: CurrentSuperUser,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """사용자 목록 조회 (관리자 전용)."""
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    total = user_crud.get_count(db)
    return UserListResponse(data=users, total=total)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    db: DbSession,
    _current_user: CurrentSuperUser,
    user_id: uuid.UUID,
) -> Any:
    """사용자 상세 조회 (관리자 전용)."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    db: DbSession,
    _current_user: CurrentSuperUser,
    user_in: UserCreate,
) -> Any:
    """사용자 생성 (관리자 전용)."""
    existing = user_crud.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다")
    user = user_crud.create(db, obj_in=user_in)
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    db: DbSession,
    _current_user: CurrentSuperUser,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """사용자 수정 (관리자 전용)."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    user = user_crud.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=Message)
def delete_user(
    db: DbSession,
    current_user: CurrentSuperUser,
    user_id: uuid.UUID,
) -> Any:
    """사용자 삭제 (관리자 전용)."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="자기 자신은 삭제할 수 없습니다")
    user_crud.delete(db, id=user_id)
    return Message(message="사용자가 삭제되었습니다")
