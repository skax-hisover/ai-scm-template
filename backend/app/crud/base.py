"""
제네릭 CRUD Base 클래스.

모든 엔티티의 공통 CRUD 작업을 제네릭으로 구현합니다.
새로운 엔티티 CRUD를 추가할 때 이 클래스를 상속받으세요.

사용 예:
    class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
        pass
    item_crud = CRUDItem(Item)
"""

import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.base import Base

# 타입 변수 정의
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    제네릭 CRUD Base.

    기본 CRUD 작업(생성, 조회, 수정, 삭제)을 제공합니다.
    엔티티별 특수 로직이 필요한 경우 메서드를 오버라이드하세요.
    """

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, *, id: uuid.UUID) -> ModelType | None:
        """ID로 단건 조회."""
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ModelType]:
        """페이지네이션 목록 조회."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = db.execute(stmt)
        return list(result.scalars().all())

    def get_count(self, db: Session) -> int:
        """전체 건수 조회."""
        stmt = select(func.count()).select_from(self.model)
        result = db.execute(stmt)
        return result.scalar_one()

    def create(self, db: Session, *, obj_in: CreateSchemaType, **extra_fields: Any) -> ModelType:
        """
        엔티티 생성.

        Args:
            db: DB 세션
            obj_in: 생성 스키마
            **extra_fields: 추가 필드 (예: owner_id)

        Returns:
            생성된 엔티티
        """
        obj_data = obj_in.model_dump()
        obj_data.update(extra_fields)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        엔티티 수정 (부분 업데이트).

        Args:
            db: DB 세션
            db_obj: 기존 DB 객체
            obj_in: 수정 스키마 (exclude_unset으로 전달된 필드만 업데이트)

        Returns:
            수정된 엔티티
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: uuid.UUID) -> ModelType | None:
        """
        엔티티 삭제.

        Returns:
            삭제된 엔티티 또는 None (존재하지 않는 경우)
        """
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
