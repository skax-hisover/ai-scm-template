"""
인증 API.

로그인, 토큰 발급/갱신 등의 인증 관련 엔드포인트를 정의합니다.

[개발 표준]
- 로그인 실패 시 구체적인 이유를 노출하지 마세요 (보안).
- 토큰은 항상 HTTPS 환경에서만 전송하세요 (프로덕션).
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DbSession
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.crud import user_crud
from app.schemas.auth import LoginRequest, RefreshTokenRequest, Token
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: DbSession,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 호환 로그인 - 액세스 토큰 발급.

    Swagger UI에서 테스트할 때는 이 엔드포인트가 사용됩니다.
    username 필드에 이메일을 입력하세요.
    """
    user = user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성 사용자입니다",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(user.id, expires_delta=access_token_expires),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login/json", response_model=Token)
def login_json(db: DbSession, login_data: LoginRequest) -> Token:
    """
    JSON Body 로그인 - 프론트엔드에서 사용.

    OAuth2 form 대신 JSON body로 로그인합니다.
    """
    user = user_crud.authenticate(
        db, email=login_data.email, password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성 사용자입니다",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(user.id, expires_delta=access_token_expires),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=Token)
def refresh_token(db: DbSession, body: RefreshTokenRequest) -> Token:
    """리프레시 토큰으로 새로운 액세스 토큰을 발급합니다."""
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다",
        )

    user = db.get(
        __import__("app.models.user", fromlist=["User"]).User,
        payload["sub"],
    )
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(user.id, expires_delta=access_token_expires),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: CurrentUser) -> UserResponse:
    """현재 로그인된 사용자 정보를 반환합니다."""
    return UserResponse.model_validate(current_user)
