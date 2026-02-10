"""
공통 스키마 정의.

모든 API에서 공통으로 사용되는 응답 스키마를 정의합니다.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Message(BaseModel):
    """공통 메시지 응답."""

    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    """
    페이지네이션 응답 스키마.

    사용 예:
        @router.get("/items", response_model=PaginatedResponse[ItemResponse])
        def list_items(...):
            return PaginatedResponse(data=items, total=total, page=page, size=size)
    """

    data: list[Any]
    total: int
    page: int = 1
    size: int = 20

    @property
    def total_pages(self) -> int:
        return (self.total + self.size - 1) // self.size if self.size > 0 else 0


class ErrorResponse(BaseModel):
    """공통 에러 응답."""

    detail: str
    error_code: str | None = None
