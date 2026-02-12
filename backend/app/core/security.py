"""
보안 관련 유틸리티 모듈.

JWT 토큰 생성/검증, 비밀번호 해싱 등을 담당합니다.

[개발 표준]
- 비밀번호는 반드시 해싱하여 저장하세요 (평문 저장 금지).
- JWT 토큰에는 민감한 정보를 포함하지 마세요 (user_id만 sub에 저장).
- 토큰 만료 시간은 settings에서 관리합니다.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# 비밀번호 해싱 컨텍스트
# bcrypt를 기본으로 사용, 향후 다른 알고리즘으로 마이그레이션 가능
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 알고리즘
ALGORITHM = "HS256"


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """
    JWT 액세스 토큰을 생성합니다.

    Args:
        subject: 토큰의 주체 (일반적으로 user_id)
        expires_delta: 만료 시간 (None이면 설정의 기본값 사용)

    Returns:
        인코딩된 JWT 문자열
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    """
    JWT 리프레시 토큰을 생성합니다.

    Args:
        subject: 토큰의 주체 (일반적으로 user_id)

    Returns:
        인코딩된 JWT 문자열
    """
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any] | None:
    """
    JWT 토큰을 디코딩합니다.

    Args:
        token: JWT 문자열

    Returns:
        디코딩된 페이로드 또는 None (유효하지 않은 경우)
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시된 비밀번호를 비교합니다."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호를 해싱합니다."""
    return pwd_context.hash(password)
