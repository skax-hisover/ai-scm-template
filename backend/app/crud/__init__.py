"""
CRUD (Create, Read, Update, Delete) 패키지.

[개발 표준]
- 모든 CRUD 클래스는 CRUDBase를 상속받습니다.
- 공통 CRUD 로직은 CRUDBase에 구현하고, 엔티티별 특수 로직만 하위 클래스에 추가합니다.
- CRUD 메서드는 DB 세션을 받아서 처리하고, commit은 호출자(API 레이어)에서 관리합니다.
"""

from app.crud.item import item_crud  # noqa: F401
from app.crud.user import user_crud  # noqa: F401
