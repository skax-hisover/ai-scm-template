"""
API 라우터 설정.

모든 v1 엔드포인트를 여기에 등록합니다.

[개발 표준]
- 새로운 API 모듈 추가 시 이 파일에 include_router를 추가하세요.
- prefix는 리소스명 복수형을 사용합니다 (예: /users, /items).
- tags는 Swagger 문서의 그룹핑에 사용됩니다.
"""

from fastapi import APIRouter

from app.api.v1 import agents, auth, health, items, users

api_router = APIRouter()

# 헬스체크 (인증 불필요)
api_router.include_router(health.router, tags=["health"])

# 인증
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 사용자 관리
api_router.include_router(users.router, prefix="/users", tags=["users"])

# 아이템 (샘플)
api_router.include_router(items.router, prefix="/items", tags=["items"])

# Agent 실행
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

# ─── 새로운 라우터 추가 위치 ─────────────────────────────────
# api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
# api_router.include_router(products.router, prefix="/products", tags=["products"])
