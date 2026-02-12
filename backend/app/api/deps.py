"""
API 의존성 (Dependency Injection) 모듈.

FastAPI의 Depends를 활용한 공통 의존성을 정의합니다.

[개발 표준]
- DB 세션은 항상 DbSession 타입 별칭을 사용하세요.
- 인증이 필요한 엔드포인트는 CurrentUser를 파라미터에 추가하세요.
- 관리자 전용 엔드포인트는 CurrentSuperUser를 사용하세요.
- 새로운 공통 의존성 추가 시 이 파일에 정의하세요.
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import ALGORITHM
from app.models.user import User
from app.schemas.auth import TokenPayload

# OAuth2 스키마 (Swagger UI에서 자물쇠 아이콘 표시)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# ─── 타입 별칭 ─────────────────────────────────────────────
DbSession = Annotated[Session, Depends(get_db)]
TokenStr = Annotated[str, Depends(oauth2_scheme)]


# ─── 현재 사용자 의존성 ───────────────────────────────────────
def get_current_user(db: DbSession, token: TokenStr) -> User:
    """
    JWT 토큰에서 현재 사용자를 추출합니다.

    사용 예:
        @router.get("/me")
        def read_me(current_user: CurrentUser):
            return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except jwt.InvalidTokenError as err:
        raise credentials_exception from err

    user = db.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="비활성 사용자입니다")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_superuser(current_user: CurrentUser) -> User:
    """관리자 권한을 확인합니다."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 부족합니다",
        )
    return current_user


CurrentSuperUser = Annotated[User, Depends(get_current_superuser)]
