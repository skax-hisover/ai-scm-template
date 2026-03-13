# 백엔드 개발 가이드

> FastAPI 기반 백엔드의 개발 환경, 개발 표준, 기능 추가 가이드, 빌드·실행·배포 방법을 정의합니다.

---

## 📋 목차

1. [개발 환경 설정](#1-개발-환경-설정)
2. [레이어 아키텍처](#2-레이어-아키텍처)
3. [새로운 기능 추가 절차](#3-새로운-기능-추가-절차)
4. [코딩 규칙](#4-코딩-규칙)
5. [핵심 모듈 가이드](#5-핵심-모듈-가이드)
6. [테스트](#6-테스트)
7. [빌드, 실행 및 종료](#7-빌드-실행-및-종료)
8. [배포](#8-배포)

---

## 1. 개발 환경 설정

### 1.1 사전 요구사항

아래 도구가 설치되어 있어야 합니다. 터미널에서 명령어를 실행하여 확인하세요.

| 도구 | 버전 | 설치 확인 | 설치 방법 |
|------|------|-----------|-----------|
| Python | ≥ 3.11 | `python --version` | [python.org](https://python.org) |
| uv | ≥ 0.10 | `uv --version` | `pip install uv` |
| Docker | — | `docker --version` | [docker.com](https://docker.com) |

> 💡 PostgreSQL과 Redis는 Docker로 실행하므로 별도 설치가 필요하지 않습니다.

### 1.2 초기 설정 (Step by Step)

> 이 절차는 **처음 프로젝트를 세팅할 때 1회만** 수행합니다.

**Step 1.** 프로젝트 루트 폴더에서 환경 변수 파일을 생성합니다.

```bash
cd ai-scm-template

# macOS / Linux
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

> 생성된 `.env` 파일은 로컬 개발 환경에서는 기본값 그대로 사용해도 됩니다.

**Step 2.** Docker Desktop이 실행 중인지 확인한 후, DB와 Redis를 시작합니다.

```bash
docker compose up -d db redis
```

> 정상 확인: `docker compose ps` 명령어로 `db`와 `redis`가 `healthy` 상태인지 확인합니다.

**Step 3.** `backend` 폴더로 이동하여 Python 의존성을 설치합니다.

```bash
cd backend
uv sync
```

> `uv sync`는 `pyproject.toml`에 정의된 모든 의존성을 설치하고 `.venv/` 가상환경을 자동 생성합니다.

### 1.3 가상환경 활성화

> 백엔드 작업 시 **매번 터미널을 새로 열 때마다** 가상환경을 활성화해야 합니다.

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\activate

# Windows (cmd)
.venv\Scripts\activate.bat
```

> ✅ 프롬프트 앞에 `(.venv)` 표시가 나타나면 성공입니다.
>
> 작업이 끝나면 `deactivate` 명령어로 가상환경을 해제할 수 있습니다.

### 1.4 DB 마이그레이션 및 초기 데이터

> 가상환경이 활성화된 상태에서 `backend/` 폴더 안에서 실행합니다.

```bash
cd backend

# DB 테이블 생성 (마이그레이션 적용)
alembic upgrade head

# 초기 관리자 계정 생성
python -m app.initial_data
```

> 정상 완료 시 `Initial data created` 또는 `Superuser already exists` 메시지가 출력됩니다.

### 1.5 주의사항 (트러블슈팅)

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| `uv sync` 시 `Unable to determine which files to ship` | Hatchling 빌드 설정 누락 | `pyproject.toml`에 `[tool.hatch.build.targets.wheel]` → `packages = ["app"]` 추가 |
| `alembic upgrade head` 시 `UnicodeDecodeError (cp949)` | Windows 한국어 로캘에서 `alembic.ini`의 한글 주석 인코딩 충돌 | `alembic.ini`의 한글 주석을 영문으로 변경 |
| `python -m app.initial_data` 시 `ValueError: password cannot be longer than 72 bytes` | `passlib`과 `bcrypt>=5.0` 호환성 문제 | `pyproject.toml`에 `"bcrypt>=4.0.0,<5.0.0"` 버전 고정 |
| DB 연결 시 `password authentication failed` (한글 에러) | 로컬 PostgreSQL과 Docker PostgreSQL의 포트(5432) 충돌 | `.env`에서 `POSTGRES_PORT=5433` 등으로 변경 |

### 1.6 의존성 관리

| 작업 | 명령어 |
|------|--------|
| 전체 의존성 설치 | `uv sync` |
| 패키지 추가 | `uv add <패키지명>` |
| 개발 의존성 추가 | `uv add --group dev <패키지명>` |
| 패키지 제거 | `uv remove <패키지명>` |

의존성은 `pyproject.toml`에서 관리합니다:

```toml
# 프로덕션 의존성
[project]
dependencies = [
    "fastapi[standard]>=0.115.0,<1.0.0",
    "passlib[bcrypt]>=1.7.4,<2.0.0",
    "bcrypt>=4.0.0,<5.0.0",             # passlib 호환을 위해 5.0 미만 고정
    ...
]

# 개발 의존성
[dependency-groups]
dev = [
    "pytest>=8.0.0,<9.0.0",
    "ruff>=0.8.0,<1.0.0",
    ...
]

# 빌드 설정 (hatchling이 app/ 패키지를 인식하도록)
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]
```

---

## 2. 레이어 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│  API Layer (api/v1/)                                    │
│  - HTTP 요청/응답 처리                                    │
│  - 인증 검증 (Depends: CurrentUser, CurrentSuperUser)    │
│  - 요청 유효성 검증 (Pydantic Schema)                     │
│  - 응답 직렬화                                            │
├─────────────────────────────────────────────────────────┤
│  CRUD Layer (crud/)                                     │
│  - 데이터 접근 로직                                       │
│  - CRUDBase 상속으로 공통 CRUD 자동 제공                   │
│  - 엔티티별 특수 쿼리 구현                                 │
├─────────────────────────────────────────────────────────┤
│  Model Layer (models/)                                  │
│  - SQLAlchemy ORM 모델                                  │
│  - Base 클래스 (UUID PK 자동 생성)                        │
│  - TimestampMixin (created_at, updated_at 자동 관리)     │
├─────────────────────────────────────────────────────────┤
│  Schema Layer (schemas/)                                │
│  - Pydantic 스키마 (DTO)                                 │
│  - Create / Update / Response 분리                      │
│  - 요청/응답 데이터 검증 및 직렬화                          │
├─────────────────────────────────────────────────────────┤
│  Core Layer (core/)                                     │
│  - config.py: 환경 설정 (pydantic-settings)              │
│  - database.py: DB 연결/세션 관리                         │
│  - security.py: JWT 토큰, 비밀번호 해싱                   │
│  - logging.py: 구조화된 JSON 로깅                         │
└─────────────────────────────────────────────────────────┘
```

### 레이어 간 호출 규칙

- **API → CRUD → Model** 방향으로만 호출
- API 레이어에서 직접 Model을 조작하지 않음
- CRUD 레이어에서 HTTP 관련 로직(HTTPException 등)을 사용하지 않음
- Schema는 API와 CRUD 양쪽에서 사용 (요청/응답 DTO)

---

## 3. 새로운 기능 추가 절차

새로운 엔티티(예: `Order`)를 추가하는 전체 절차입니다.

### Step 1. Model 정의 (`models/order.py`)

```python
"""주문 모델."""

from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Order(TimestampMixin, Base):
    """주문 모델."""

    __tablename__ = "orders"

    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="주문명")
    quantity: Mapped[int] = mapped_column(Integer, default=1, comment="수량")
    owner_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, comment="주문자 ID"
    )
```

### Step 2. 모델 등록 (`models/__init__.py`)

```python
from app.models.order import Order  # noqa: F401  ← 추가
```

### Step 3. Schema 정의 (`schemas/order.py`)

```python
"""주문 스키마."""

import uuid
from datetime import datetime
from pydantic import BaseModel


class OrderCreate(BaseModel):
    title: str
    quantity: int = 1


class OrderUpdate(BaseModel):
    title: str | None = None
    quantity: int | None = None


class OrderResponse(BaseModel):
    id: uuid.UUID
    title: str
    quantity: int
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### Step 4. CRUD 생성 (`crud/order.py`)

```python
"""주문 CRUD."""

from app.crud.base import CRUDBase
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    """주문 CRUD. 특수 쿼리가 필요하면 여기에 메서드를 추가하세요."""
    pass


order_crud = CRUDOrder(Order)
```

### Step 5. API 생성 (`api/v1/orders.py`)

```python
"""주문 API."""

import uuid
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.crud.order import order_crud
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(*, db: DbSession, current_user: CurrentUser, order_in: OrderCreate):
    """주문을 생성합니다."""
    return order_crud.create(db, obj_in=order_in, owner_id=current_user.id)


@router.get("/", response_model=list[OrderResponse])
def read_orders(*, db: DbSession, current_user: CurrentUser, skip: int = 0, limit: int = 20):
    """주문 목록을 조회합니다."""
    return order_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderResponse)
def read_order(*, db: DbSession, current_user: CurrentUser, order_id: uuid.UUID):
    """주문을 상세 조회합니다."""
    order = order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return order
```

### Step 6. 라우터 등록 (`api/router.py`)

```python
from app.api.v1 import orders  # 추가

# 주문
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
```

### Step 7. DB 마이그레이션

```bash
cd backend

# 마이그레이션 파일 자동 생성
alembic revision --autogenerate -m "add orders table"

# 마이그레이션 적용
alembic upgrade head
```

### Step 8. 테스트 작성

```bash
# tests/test_orders.py 작성 후
pytest tests/test_orders.py -v
```

---

## 4. 코딩 규칙

### 4.1 코드 품질 도구

| 도구 | 역할 | 설정 파일 |
|------|------|-----------|
| **Ruff** | Formatter + Linter | `pyproject.toml` |
| **MyPy** | 타입 검사 (strict 모드) | `pyproject.toml` |
| **Pytest** | 테스트 프레임워크 | `pyproject.toml` |

### 4.2 실행 방법

```bash
cd backend

# 포맷팅 (자동 수정)
ruff format .

# 린트 검사
ruff check .

# 린트 자동 수정
ruff check --fix .

# 타입 검사
mypy app/

# 전체 테스트
pytest
```

### 4.3 Ruff 규칙

`pyproject.toml`에 설정된 주요 규칙:

| 규칙 ID | 설명 |
|---------|------|
| `E`, `W` | pycodestyle (코드 스타일) |
| `F` | pyflakes (미사용 import 등) |
| `I` | isort (import 정렬) |
| `B` | flake8-bugbear (잠재적 버그) |
| `C4` | flake8-comprehensions (컴프리헨션 검사) |
| `T201` | print 문 사용 금지 |
| `N` | PEP 8 네이밍 |
| `UP` | pyupgrade (최신 문법 사용) |
| `ARG001` | unused arguments (미사용 인자 검사) |
| `SIM` | flake8-simplify (코드 단순화) |

### 4.4 네이밍 컨벤션

| 대상 | 규칙 | 예시 |
|------|------|------|
| 변수 / 함수 | `snake_case` | `get_user_by_id` |
| 클래스 | `PascalCase` | `CRUDOrder`, `OrderCreate` |
| 상수 | `UPPER_SNAKE_CASE` | `ALGORITHM`, `EXCLUDE_PATHS` |
| 모듈 / 파일명 | `snake_case` | `order.py`, `date_utils.py` |

### 4.5 Docstring 규칙

- 모든 **모듈**, **클래스**, **공개 함수**에 docstring을 작성합니다.
- 모듈 docstring 상단에 `[개발 표준]` 섹션을 포함합니다.

```python
"""
주문 관련 CRUD 모듈.

[개발 표준]
- CRUDBase를 상속하여 공통 CRUD를 재사용합니다.
- 엔티티별 특수 쿼리는 해당 CRUD 클래스에 추가합니다.
"""
```

### 4.6 Line Length

- **120자** (`pyproject.toml` → `[tool.ruff]` → `line-length = 120`)

---

## 5. 핵심 모듈 가이드

### 5.1 환경 설정 (`core/config.py`)

- `pydantic-settings`의 `BaseSettings`를 상속한 `Settings` 클래스
- `.env` 파일 또는 시스템 환경 변수에서 자동으로 값을 로드
- 환경별 분기: `settings.ENVIRONMENT` (`local` / `staging` / `production`)
- 보안 검증: `changethis` 기본값 사용 시 `local` 외 환경에서 에러 발생

```python
from app.core.config import settings

# 설정 사용
print(settings.PROJECT_NAME)       # "AI-SCM"
print(settings.database_url)       # 자동 생성된 PostgreSQL URL
print(settings.ENVIRONMENT)        # "local"
```

### 5.2 DB 세션 (`core/database.py`)

- `SessionLocal`: SQLAlchemy 세션 팩토리
- `get_db()`: FastAPI Depends용 세션 제너레이터
- 커넥션 풀: `pool_size=10`, `max_overflow=20`

```python
# API 엔드포인트에서 사용
from app.api.deps import DbSession

@router.get("/items")
def get_items(db: DbSession):  # 자동 DI
    ...
```

### 5.3 인증 / 보안 (`core/security.py`, `api/deps.py`)

#### JWT 토큰

| 토큰 | 만료 시간 | 용도 |
|------|-----------|------|
| Access Token | 24시간 (설정 변경 가능) | API 인증 |
| Refresh Token | 7일 | Access Token 재발급 |

#### 인증 의존성

| 의존성 | 용도 |
|--------|------|
| `DbSession` | DB 세션 주입 |
| `CurrentUser` | 인증된 현재 사용자 |
| `CurrentSuperUser` | 관리자 권한 확인 |

```python
from app.api.deps import CurrentUser, CurrentSuperUser, DbSession

# 인증 필요
@router.get("/profile")
def get_profile(current_user: CurrentUser):
    return current_user

# 관리자만 접근 가능
@router.delete("/{user_id}")
def delete_user(current_user: CurrentSuperUser, user_id: uuid.UUID):
    ...
```

#### 비밀번호 해싱

```python
from app.core.security import get_password_hash, verify_password

hashed = get_password_hash("mypassword")
is_valid = verify_password("mypassword", hashed)  # True
```

### 5.4 로깅 (`core/logging.py`)

- JSON 형식의 구조화된 로그 출력
- **`print()` 사용 금지** → `logger` 사용 (Ruff `T201` 규칙으로 검사)

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# ✅ Good
logger.info("사용자 생성 완료", extra={"user_id": str(user.id), "email": user.email})
logger.error("주문 처리 실패", extra={"order_id": str(order.id)}, exc_info=True)

# ❌ Bad
print("사용자 생성 완료")
logger.info(f"사용자 {user.email} 생성 완료")  # extra 사용 권장
```

#### 로그 레벨 가이드

| 레벨 | 용도 |
|------|------|
| `DEBUG` | 개발 디버깅용 상세 정보 |
| `INFO` | 정상 동작 확인 (API 호출, 작업 완료) |
| `WARNING` | 비정상이지만 처리 가능한 상황 |
| `ERROR` | 오류 발생 (예외 처리됨) |
| `CRITICAL` | 시스템 중단 수준의 심각한 오류 |

### 5.5 제네릭 CRUD Base (`crud/base.py`)

`CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]`를 상속하면 다음 메서드가 자동 제공됩니다:

| 메서드 | 설명 |
|--------|------|
| `get(db, id=...)` | ID로 단건 조회 |
| `get_multi(db, skip=0, limit=20)` | 페이지네이션 목록 조회 |
| `get_count(db)` | 전체 건수 조회 |
| `create(db, obj_in=..., **extra)` | 엔티티 생성 |
| `update(db, db_obj=..., obj_in=...)` | 엔티티 수정 (부분 업데이트) |
| `delete(db, id=...)` | 엔티티 삭제 |

특수 쿼리가 필요하면 해당 CRUD 클래스에 메서드를 추가합니다:

```python
class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return db.execute(stmt).scalars().first()
```

### 5.6 미들웨어

| 미들웨어 | 파일 | 설명 |
|----------|------|------|
| CORS | `main.py` | 프론트엔드 도메인 허용 |
| Logging | `middleware/logging_middleware.py` | 요청/응답 JSON 로깅, 요청 ID 자동 생성 |
| Error Handler | `middleware/error_handler.py` | 전역 예외 → 일관된 에러 응답 |

### 5.7 Celery 비동기 태스크 (`tasks/`)

```python
from app.tasks.celery_app import celery_app

@celery_app.task
def send_notification(user_id: str, message: str):
    """비동기로 알림을 전송합니다."""
    ...

# API에서 태스크 호출
send_notification.delay(str(user.id), "주문이 완료되었습니다")
```

Celery 워커 실행 및 종료:

```bash
# 워커 시작 (별도 터미널에서 실행, 가상환경 활성화 필요)
cd backend
celery -A app.tasks.celery_app worker --loglevel=info

# 종료: Ctrl+C 입력
```

### 5.8 Agent 플랫폼 연동 (`services/agent_client.py`, `api/v1/agents.py`)

현재 템플릿에는 Agent 플랫폼 연동 v1이 포함되어 있습니다.

구성 파일:

- `models/agent_run.py`: Agent 실행 이력 모델
- `schemas/agent.py`: 실행 요청/응답 스키마
- `crud/agent_run.py`: 실행 이력 CRUD 및 상태 전환
- `services/agent_client.py`: 외부 Agent 플랫폼 호출 클라이언트
- `tasks/agent_tasks.py`: 비동기 실행 태스크
- `api/v1/agents.py`: Agent 실행 API

제공 API:

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/v1/agents/runs` | Agent 실행 요청 생성 (동기/비동기) |
| GET | `/api/v1/agents/runs` | 실행 이력 목록 조회 |
| GET | `/api/v1/agents/runs/{run_id}` | 실행 이력 단건 조회 |

연동 흐름 다이어그램:

```
[Frontend: /dashboard/agents]
            │ POST /api/v1/agents/runs
            ▼
[FastAPI: api/v1/agents.py]
            │ run 생성(status=queued)
            │ delay(run_id)
            ▼
[Celery: tasks/agent_tasks.py]
            │ status=running
            │ HTTP call
            ▼
[External Agent Platform API]
            │ result / error
            ▼
[PostgreSQL: agent_runs]
            │ status=succeeded|failed, output_text/error_message 저장
            ▼
[FastAPI 조회 API]
            │ GET /api/v1/agents/runs/{run_id}
            ▼
[Frontend 결과 표시]
```

관련 환경 변수:

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `AGENT_PLATFORM_BASE_URL` | Agent 플랫폼 API Base URL | — |
| `AGENT_PLATFORM_API_KEY` | Agent 플랫폼 인증 키 | — |
| `AGENT_PLATFORM_RUN_PATH` | 실행 API 경로 | `/v1/agents/runs` |
| `AGENT_REQUEST_TIMEOUT_SECONDS` | Agent API 요청 타임아웃(초) | `60` |
| `AGENT_DEFAULT_MODEL` | 기본 모델명 | `default` |

---

## 6. 테스트

### 6.1 테스트 환경

- **인메모리 SQLite** 사용 (실제 DB 격리)
- `conftest.py`에 DB 세션, 테스트 클라이언트 fixture 정의
- 각 테스트는 독립적으로 실행 (테스트 전 테이블 생성, 후 삭제)

### 6.2 테스트 실행

```bash
cd backend

# 전체 테스트
pytest

# 상세 출력
pytest -v

# 커버리지 측정
pytest --cov=app

# 특정 파일만 실행
pytest tests/test_health.py

# 특정 테스트만 실행
pytest tests/test_health.py::test_health_check -v
```

### 6.3 테스트 규칙

- **커버리지 목표: 80% 이상** (`pyproject.toml` → `fail_under = 80`)
- API 엔드포인트별 최소 1개 이상의 테스트 작성
- 테스트 파일명: `test_*.py`
- 테스트 함수명: `test_*`
- 테스트 클래스명: `Test*`

### 6.4 테스트 작성 예시

```python
"""주문 API 테스트."""

def test_create_order(client):
    """주문 생성 테스트."""
    response = client.post(
        "/api/v1/orders/",
        json={"title": "테스트 주문", "quantity": 5},
        headers={"Authorization": "Bearer <token>"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "테스트 주문"
    assert data["quantity"] == 5
```

---

## 7. 빌드, 실행 및 종료

### 7.1 개발 서버 실행

> 개발 서버는 코드를 수정하면 **자동으로 재시작**(Hot Reload)됩니다.
> 가상환경이 활성화된 상태에서 `backend/` 폴더 안에서 실행하세요.

```bash
cd backend

# uvicorn (자동 리로드)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 FastAPI CLI (개발 모드 - 자동 리로드 포함)
fastapi dev app/main.py
```

> ✅ `Uvicorn running on http://0.0.0.0:8000` 메시지가 나타나면 정상입니다.
> 브라우저에서 http://localhost:8000/docs 에 접속하면 Swagger API 문서를 확인할 수 있습니다.

### 7.2 개발 서버 종료

```bash
# 실행 중인 터미널에서 Ctrl+C를 눌러 서버를 종료합니다.
# 이후 가상환경을 해제합니다.
deactivate
```

> 💡 `Ctrl+C`: 키보드에서 `Ctrl` 키를 누른 채 `C` 키를 누릅니다. 현재 실행 중인 프로그램을 중단합니다.

#### 전체 종료 절차 (로컬 개발 환경)

| 순서 | 대상 | 종료 방법 |
|:----:|------|-----------|
| ① | **백엔드 서버** | 터미널에서 `Ctrl + C` 입력 |
| ② | **가상환경 해제** | `deactivate` 입력 |
| ③ | **Celery 워커** (실행한 경우) | 해당 터미널에서 `Ctrl + C` 입력 |
| ④ | **DB + Redis (Docker)** | `docker compose down` 실행 (프로젝트 루트에서) |

```bash
# 프로젝트 루트 폴더에서 실행
cd ai-scm-template

# DB + Redis 컨테이너 종료 (데이터 유지)
docker compose down

# DB + Redis 컨테이너 종료 + 데이터 삭제 (DB 초기화 시 사용)
docker compose down -v
```

### 7.3 Docker 빌드

> Docker 이미지를 직접 빌드하는 방법입니다. **프로젝트 루트 폴더**에서 실행하세요.

```bash
# 백엔드 이미지 빌드
docker build -f backend/Dockerfile -t ai-scm-backend .

# 빌드된 이미지 실행
docker run -p 8000:8000 \
  -e POSTGRES_SERVER=host.docker.internal \
  -e POSTGRES_PASSWORD=changethis \
  ai-scm-backend

# 종료: 다른 터미널에서
docker ps                              # 실행 중인 컨테이너 ID 확인
docker stop <CONTAINER_ID>             # 컨테이너 종료
```

### 7.4 Docker Compose

```bash
# 전체 서비스 빌드 및 실행
docker compose up -d --build

# 백엔드만 재빌드
docker compose up -d --build backend

# 로그 확인
docker compose logs -f backend

# 종료
docker compose down
```

### 7.5 프로덕션 실행

Dockerfile의 기본 CMD는 프로덕션 설정입니다:

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

- `--workers 4`: CPU 코어 수에 맞게 조절
- `--reload` 옵션 없음 (프로덕션에서는 사용하지 않음)

---

## 8. 배포

### 8.1 배포 전 체크리스트

- [ ] 환경 변수 확인: `ENVIRONMENT`를 `staging` 또는 `production`으로 설정
- [ ] 시크릿 변경: `SECRET_KEY`, `POSTGRES_PASSWORD`, `FIRST_SUPERUSER_PASSWORD`
- [ ] DB 마이그레이션: `alembic upgrade head` 실행
- [ ] 초기 데이터: `python -m app.initial_data` 실행
- [ ] 테스트 통과: `pytest --cov=app` (커버리지 80% 이상)
- [ ] 린트 통과: `ruff check .`
- [ ] 타입 체크 통과: `mypy app/`
- [ ] CORS 설정: `BACKEND_CORS_ORIGINS`에 프로덕션 도메인 추가
- [ ] Sentry 설정: `SENTRY_DSN` 설정 (선택)

### 8.2 환경별 동작 차이

| 항목 | local | staging / production |
|------|-------|---------------------|
| 시크릿 기본값 사용 | ⚠️ 경고 출력 | ❌ 에러 발생 |
| SQL 로그 출력 | ✅ (echo=True) | ❌ |
| 에러 상세 응답 | ✅ (상세 메시지) | ❌ ("서버 내부 오류") |
| Sentry | ❌ | ✅ (DSN 설정 시) |

### 8.3 Docker 기반 배포

```bash
# 프로덕션 이미지 빌드
docker build -f backend/Dockerfile -t ai-scm-backend:latest .

# 레지스트리 푸시
docker tag ai-scm-backend:latest <registry>/ai-scm-backend:latest
docker push <registry>/ai-scm-backend:latest
```

### 8.4 prestart.sh

`backend/scripts/prestart.sh`는 서버 시작 전 DB 마이그레이션과 초기 데이터 생성을 자동 실행합니다. CI/CD 파이프라인이나 컨테이너 시작 스크립트에서 활용하세요:

```bash
#!/bin/bash
set -e
alembic upgrade head
python -m app.initial_data
```

---

> **📌 참고**: 이 가이드는 프로젝트 진행에 따라 지속적으로 업데이트됩니다. 문의 사항이 있으면 팀 채널에서 논의해주세요.
>
> ← [README.md (프로젝트 개요)](../README.md)로 돌아가기
