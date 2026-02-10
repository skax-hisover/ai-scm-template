"""
사용자 CRUD.

인증/비밀번호 관련 특수 로직을 포함합니다.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """사용자 전용 CRUD."""

    def get_by_email(self, db: Session, *, email: str) -> User | None:
        """이메일로 사용자 조회."""
        stmt = select(User).where(User.email == email)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def create(self, db: Session, *, obj_in: UserCreate, **extra_fields) -> User:  # type: ignore[override]
        """사용자 생성 (비밀번호 해싱 처리)."""
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:  # type: ignore[override]
        """사용자 수정 (비밀번호 변경 시 해싱 처리)."""
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data.pop("password"))
            update_data["hashed_password"] = hashed_password
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> User | None:
        """이메일/비밀번호로 인증."""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """사용자 활성 상태 확인."""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """관리자 여부 확인."""
        return user.is_superuser


# 싱글턴 인스턴스
user_crud = CRUDUser(User)
