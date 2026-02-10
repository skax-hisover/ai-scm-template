"""
아이템 API (샘플 CRUD).

새로운 비즈니스 API를 추가할 때 이 파일을 참고 템플릿으로 사용하세요.

[개발 표준]
- 모든 엔드포인트에 response_model을 명시하세요.
- 권한 검증은 의존성 또는 엔드포인트 내부에서 수행합니다.
- 에러 응답은 HTTPException으로 처리하세요.
"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, DbSession
from app.crud import item_crud
from app.schemas.common import Message
from app.schemas.item import ItemCreate, ItemListResponse, ItemResponse, ItemUpdate

router = APIRouter()


@router.get("/", response_model=ItemListResponse)
def list_items(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """
    아이템 목록 조회.

    - 관리자: 전체 아이템 조회
    - 일반 사용자: 자신의 아이템만 조회
    """
    if current_user.is_superuser:
        items = item_crud.get_multi(db, skip=skip, limit=limit)
        total = item_crud.get_count(db)
    else:
        items = item_crud.get_by_owner(
            db, owner_id=current_user.id, skip=skip, limit=limit
        )
        total = item_crud.get_count_by_owner(db, owner_id=current_user.id)
    return ItemListResponse(data=items, total=total)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    db: DbSession,
    current_user: CurrentUser,
    item_id: uuid.UUID,
) -> Any:
    """아이템 상세 조회."""
    item = item_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 부족합니다")
    return item


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(
    db: DbSession,
    current_user: CurrentUser,
    item_in: ItemCreate,
) -> Any:
    """아이템 생성."""
    item = item_crud.create_with_owner(db, obj_in=item_in, owner_id=current_user.id)
    return item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    db: DbSession,
    current_user: CurrentUser,
    item_id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """아이템 수정."""
    item = item_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 부족합니다")
    item = item_crud.update(db, db_obj=item, obj_in=item_in)
    return item


@router.delete("/{item_id}", response_model=Message)
def delete_item(
    db: DbSession,
    current_user: CurrentUser,
    item_id: uuid.UUID,
) -> Any:
    """아이템 삭제."""
    item = item_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 부족합니다")
    item_crud.delete(db, id=item_id)
    return Message(message="아이템이 삭제되었습니다")
