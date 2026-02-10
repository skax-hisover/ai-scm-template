"""
인증 관련 스키마.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """로그인 응답 - JWT 토큰."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT 토큰 페이로드."""

    sub: str | None = None
    type: str | None = None


class LoginRequest(BaseModel):
    """로그인 요청 (JSON body 방식)."""

    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    """토큰 리프레시 요청."""

    refresh_token: str
