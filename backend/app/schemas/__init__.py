"""
Pydantic 스키마 (DTO) 패키지.

[개발 표준]
- 스키마는 API 요청/응답 데이터의 유효성 검증과 직렬화를 담당합니다.
- 네이밍 규칙:
    - XxxCreate: 생성 요청 스키마
    - XxxUpdate: 수정 요청 스키마
    - XxxResponse: 응답 스키마
    - XxxInDB: DB 저장 형태 (내부용)
- ORM 모델과 혼동하지 마세요. 스키마는 API 계층 전용입니다.
"""

from app.schemas.auth import Token, TokenPayload  # noqa: F401
from app.schemas.common import Message, PaginatedResponse  # noqa: F401
from app.schemas.item import (  # noqa: F401
    ItemCreate,
    ItemListResponse,
    ItemResponse,
    ItemUpdate,
)
from app.schemas.user import (  # noqa: F401
    UserCreate,
    UserResponse,
    UserUpdate,
)
