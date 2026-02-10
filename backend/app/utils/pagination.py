"""
페이지네이션 유틸리티.

API에서 목록 조회 시 공통으로 사용하는 페이지네이션 로직입니다.

사용 예:
    @router.get("/items")
    def list_items(db: DbSession, pagination: PaginationParams = Depends()):
        items = item_crud.get_multi(db, skip=pagination.skip, limit=pagination.size)
        total = item_crud.get_count(db)
        return paginate(items, total, pagination)
"""

from dataclasses import dataclass
from typing import Any

from fastapi import Query


@dataclass
class PaginationParams:
    """페이지네이션 쿼리 파라미터."""

    page: int = Query(1, ge=1, description="페이지 번호")
    size: int = Query(20, ge=1, le=100, description="페이지 크기")

    @property
    def skip(self) -> int:
        """offset 값 계산."""
        return (self.page - 1) * self.size


def paginate(
    data: list[Any],
    total: int,
    params: PaginationParams,
) -> dict[str, Any]:
    """
    페이지네이션 응답을 생성합니다.

    Returns:
        {"data": [...], "total": 100, "page": 1, "size": 20}
    """
    return {
        "data": data,
        "total": total,
        "page": params.page,
        "size": params.size,
    }
