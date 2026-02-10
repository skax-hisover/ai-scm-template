"""
아이템 CRUD (샘플).

새로운 비즈니스 엔티티의 CRUD를 추가할 때 이 파일을 참고하세요.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    """아이템 전용 CRUD."""

    def get_by_owner(
        self,
        db: Session,
        *,
        owner_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Item]:
        """소유자별 아이템 목록 조회."""
        stmt = (
            select(Item)
            .where(Item.owner_id == owner_id)
            .order_by(Item.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(stmt)
        return list(result.scalars().all())

    def get_count_by_owner(self, db: Session, *, owner_id: uuid.UUID) -> int:
        """소유자별 아이템 건수 조회."""
        stmt = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == owner_id)
        )
        result = db.execute(stmt)
        return result.scalar_one()

    def create_with_owner(
        self,
        db: Session,
        *,
        obj_in: ItemCreate,
        owner_id: uuid.UUID,
    ) -> Item:
        """소유자 지정 아이템 생성."""
        return self.create(db, obj_in=obj_in, owner_id=owner_id)


# 싱글턴 인스턴스
item_crud = CRUDItem(Item)
