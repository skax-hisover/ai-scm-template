# AI-SCM 프로젝트 개발 표준 가이드

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [기술 스택](#2-기술-스택)
3. [프로젝트 구조](#3-프로젝트-구조)
4. [개발 환경 설정](#4-개발-환경-설정)
5. [백엔드 개발 표준](#5-백엔드-개발-표준)
6. [프론트엔드 개발 표준](#6-프론트엔드-개발-표준)
7. [API 설계 규칙](#7-api-설계-규칙)
8. [데이터베이스 규칙](#8-데이터베이스-규칙)
9. [Git 컨벤션](#9-git-컨벤션)
10. [테스트 표준](#10-테스트-표준)

---

## 1. 프로젝트 개요

AI-SCM은 AI 기반 공급망 관리 시스템입니다. 본 문서는 개발자들이 일관된 코드 품질과 구조를 유지하면서 개발을 진행할 수 있도록 개발 표준을 정의합니다.

---

## 2. 기술 스택

| 구분 | 기술 | 버전 |
|------|------|------|
| **백엔드 프레임워크** | FastAPI | ≥ 0.115 |
| **ORM** | SQLAlchemy | ≥ 2.0 |
| **DB 마이그레이션** | Alembic | ≥ 1.14 |
| **비동기 태스크** | Celery + Redis | ≥ 5.4 |
| **인증** | JWT (PyJWT) | ≥ 2.8 |
| **프론트엔드** | Next.js + React + TypeScript | ≥ 15.1 |
| **HTTP 클라이언트** | Axios | ≥ 1.7 |
| **데이터베이스** | PostgreSQL | ≥ 16 |
| **패키지 관리 (BE)** | uv | ≥ 0.10 |
| **패키지 관리 (FE)** | npm | ≥ 10 |
| **Python** | Python | ≥ 3.11 |
| **Node.js** | Node.js | ≥ 20 |

---

## 3. 프로젝트 구조

```
ai-scm-template/
├── .env.example                    # 환경 변수 템플릿
├── .gitignore
├── docker-compose.yml              # Docker Compose (로컬 개발)
│
├── backend/                        # ─── 백엔드 ───
│   ├── Dockerfile
│   ├── pyproject.toml              # Python 의존성 및 도구 설정
│   ├── alembic.ini                 # Alembic 설정
│   ├── scripts/
│   │   └── prestart.sh             # 서버 시작 전 스크립트
│   ├── tests/                      # 테스트
│   │   ├── conftest.py
│   │   └── test_health.py
│   └── app/
│       ├── main.py                 # ✨ FastAPI 엔트리포인트
│       ├── initial_data.py         # 초기 데이터 생성
│       ├── core/                   # 핵심 설정
│       │   ├── config.py           # 환경 설정 (pydantic-settings)
│       │   ├── database.py         # DB 연결/세션
│       │   ├── security.py         # JWT, 비밀번호 해싱
│       │   └── logging.py          # 구조화된 로깅
│       ├── models/                 # SQLAlchemy ORM 모델
│       │   ├── base.py             # Base 클래스, TimestampMixin
│       │   ├── user.py             # 사용자 모델
│       │   └── item.py             # 아이템 모델 (샘플)
│       ├── schemas/                # Pydantic 스키마 (DTO)
│       │   ├── common.py           # 공통 (Message, Pagination)
│       │   ├── auth.py             # 인증 (Token, Login)
│       │   ├── user.py             # 사용자 스키마
│       │   └── item.py             # 아이템 스키마 (샘플)
│       ├── crud/                   # CRUD 레이어
│       │   ├── base.py             # 제네릭 CRUD Base
│       │   ├── user.py             # 사용자 CRUD
│       │   └── item.py             # 아이템 CRUD (샘플)
│       ├── api/                    # API 엔드포인트
│       │   ├── deps.py             # 의존성 (인증, DB세션)
│       │   ├── router.py           # 라우터 등록
│       │   └── v1/                 # API v1
│       │       ├── health.py       # 헬스체크
│       │       ├── auth.py         # 인증 API
│       │       ├── users.py        # 사용자 API
│       │       └── items.py        # 아이템 API (샘플)
│       ├── middleware/             # 미들웨어
│       │   ├── logging_middleware.py
│       │   └── error_handler.py
│       ├── tasks/                  # Celery 비동기 태스크
│       │   ├── celery_app.py       # Celery 설정
│       │   └── sample_tasks.py     # 샘플 태스크
│       ├── utils/                  # 공통 유틸리티
│       │   ├── datetime_utils.py
│       │   ├── string_utils.py
│       │   └── pagination.py
│       └── alembic/                # DB 마이그레이션
│           ├── env.py
│           ├── script.py.mako
│           └── versions/
│
├── frontend/                       # ─── 프론트엔드 ───
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   └── src/
│       ├── app/                    # Next.js App Router
│       │   ├── layout.tsx          # 루트 레이아웃
│       │   ├── page.tsx            # 루트 페이지 (리다이렉트)
│       │   ├── login/page.tsx      # 로그인 페이지
│       │   └── dashboard/          # 대시보드 (인증 필요)
│       │       ├── layout.tsx      # 대시보드 레이아웃 (사이드바)
│       │       ├── page.tsx        # 대시보드 메인
│       │       └── items/page.tsx  # 아이템 관리 (샘플)
│       ├── components/
│       │   └── ui/                 # 공통 UI 컴포넌트
│       │       ├── Button.tsx
│       │       └── Input.tsx
│       ├── lib/
│       │   ├── api/                # API 클라이언트
│       │   │   ├── client.ts       # Axios 인스턴스 (인터셉터)
│       │   │   ├── auth.ts         # 인증 API
│       │   │   └── items.ts        # 아이템 API (샘플)
│       │   └── auth/
│       │       └── token.ts        # JWT 토큰 관리
│       └── hooks/
│           └── useAuth.ts          # 인증 훅
│
└── docs/
    └── DEVELOPMENT_GUIDE.md        # 본 문서
```

---

## 4. 개발 환경 설정

### 4.1 사전 요구사항

| 도구 | 용도 | 설치 |
|------|------|------|
| Python ≥ 3.11 | 백엔드 런타임 | python.org |
| Node.js ≥ 20 | 프론트엔드 런타임 | nodejs.org |
| uv | Python 패키지 관리 | `pip install uv` |
| PostgreSQL ≥ 16 | 데이터베이스 | postgresql.org |
| Redis | Celery 브로커 | redis.io |
| Docker (선택) | 컨테이너 실행 | docker.com |

### 4.2 방법 A: 로컬 직접 실행

```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일을 환경에 맞게 수정

# 2. 백엔드 설정
cd backend
uv sync                         # 의존성 설치
source .venv/bin/activate       # 가상환경 활성화 (Windows: .venv\Scripts\activate)
alembic upgrade head            # DB 마이그레이션
python -m app.initial_data      # 초기 데이터 생성
uvicorn app.main:app --reload --port 8000   # 서버 시작

# 3. Celery 워커 (별도 터미널)
cd backend
celery -A app.tasks.celery_app worker --loglevel=info

# 4. 프론트엔드 (별도 터미널)
cd frontend
npm install                     # 의존성 설치
npm run dev                     # 개발 서버 시작 → http://localhost:3000
```

### 4.3 방법 B: Docker Compose

```bash
# DB + Redis만 Docker로 (백엔드/프론트엔드는 로컬)
docker compose up -d db redis

# 전체 서비스 Docker로
docker compose up -d
```

### 4.4 접속 URL

| 서비스 | URL |
|--------|-----|
| 프론트엔드 | http://localhost:3000 |
| 백엔드 API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| pgAdmin | http://localhost:5050 |

### 4.5 기본 관리자 계정

| 항목 | 값 |
|------|-----|
| 이메일 | admin@ai-scm.com |
| 비밀번호 | changethis |

---

## 5. 백엔드 개발 표준

### 5.1 레이어 아키텍처

```
API Layer (api/v1/)    ← HTTP 요청/응답 처리, 인증 검증
    ↓
CRUD Layer (crud/)     ← 데이터 접근 로직
    ↓
Model Layer (models/)  ← SQLAlchemy ORM 모델
    ↓
Database              ← PostgreSQL
```

### 5.2 새로운 기능 추가 절차

1. **Model 정의** → `models/` 에 SQLAlchemy 모델 생성
2. **Schema 정의** → `schemas/` 에 Pydantic 스키마 (Create, Update, Response) 생성
3. **CRUD 생성** → `crud/` 에 CRUDBase를 상속한 CRUD 클래스 생성
4. **API 생성** → `api/v1/` 에 라우터 생성
5. **라우터 등록** → `api/router.py` 에 `include_router` 추가
6. **마이그레이션** → `alembic revision --autogenerate -m "설명"` → `alembic upgrade head`
7. **모델 등록** → `models/__init__.py` 에 import 추가

### 5.3 코딩 규칙

| 규칙 | 설명 |
|------|------|
| **Formatter** | Ruff (자동 포맷팅) |
| **Linter** | Ruff (코드 품질 검사) |
| **Type Checker** | MyPy (strict 모드) |
| **Line Length** | 120자 |
| **Naming** | snake_case (변수/함수), PascalCase (클래스) |
| **Docstring** | 모든 모듈/클래스/공개 함수에 작성 |
| **print 금지** | logger를 사용하세요 |

### 5.4 로깅 규칙

```python
from app.core.logging import get_logger
logger = get_logger(__name__)

# ✅ Good
logger.info("사용자 생성 완료", extra={"user_id": str(user.id), "email": user.email})

# ❌ Bad
print("사용자 생성 완료")
logger.info(f"사용자 {user.email} 생성 완료")  # extra 사용 권장
```

### 5.5 환경 변수 규칙

- 모든 설정은 `core/config.py`의 Settings 클래스에 정의
- 하드코딩 금지, 반드시 환경 변수 사용
- 새로운 환경 변수 추가 시 `.env.example`에도 반영

---

## 6. 프론트엔드 개발 표준

### 6.1 디렉터리 규칙

| 경로 | 용도 |
|------|------|
| `src/app/` | 페이지 (Next.js App Router) |
| `src/components/ui/` | 공통 UI 컴포넌트 (Button, Input 등) |
| `src/components/features/` | 기능별 컴포넌트 |
| `src/lib/api/` | API 호출 함수 |
| `src/lib/auth/` | 인증 관련 유틸리티 |
| `src/hooks/` | 커스텀 훅 |
| `src/types/` | TypeScript 타입 정의 |

### 6.2 API 호출 규칙

```typescript
// ✅ Good - apiClient 인스턴스 사용
import apiClient from "@/lib/api/client";
const response = await apiClient.get("/items");

// ❌ Bad - axios 직접 사용
import axios from "axios";
const response = await axios.get("http://localhost:8000/api/v1/items");
```

### 6.3 인증 흐름

1. 로그인 → JWT 토큰 발급 → localStorage 저장
2. API 호출 → Axios 인터셉터가 자동으로 Authorization 헤더 주입
3. 401 응답 → 리프레시 토큰으로 재발급 시도 → 실패 시 로그아웃

### 6.4 코딩 규칙

| 규칙 | 설명 |
|------|------|
| **언어** | TypeScript (strict 모드) |
| **Linter** | ESLint (next 설정) |
| **스타일** | Tailwind CSS |
| **Naming** | camelCase (변수/함수), PascalCase (컴포넌트) |
| **컴포넌트** | 함수형 컴포넌트 + Hooks 사용 |
| **상태관리** | React Hooks (필요 시 Context API) |

---

## 7. API 설계 규칙

### 7.1 URL 규칙

| 규칙 | 예시 |
|------|------|
| 리소스명은 복수형 | `/api/v1/items` |
| 하이픈 사용 금지 | `/api/v1/order-items` ❌ → `/api/v1/order_items` ✅ |
| 동사 사용 금지 | `/api/v1/get_items` ❌ → `GET /api/v1/items` ✅ |
| ID는 경로 파라미터 | `/api/v1/items/{item_id}` |

### 7.2 HTTP 메서드

| 메서드 | 용도 | 응답 코드 |
|--------|------|-----------|
| GET | 조회 | 200 |
| POST | 생성 | 201 |
| PUT | 전체 수정 | 200 |
| PATCH | 부분 수정 | 200 |
| DELETE | 삭제 | 200 |

### 7.3 응답 형식

```json
// 단건 응답
{
  "id": "uuid",
  "title": "아이템",
  "created_at": "2026-01-01T00:00:00Z"
}

// 목록 응답
{
  "data": [...],
  "total": 100,
  "page": 1,
  "size": 20
}

// 에러 응답
{
  "detail": "에러 메시지"
}
```

---

## 8. 데이터베이스 규칙

### 8.1 네이밍 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| 테이블명 | snake_case 복수형 | `users`, `order_items` |
| 컬럼명 | snake_case | `created_at`, `owner_id` |
| PK | `id` (UUID) | - |
| FK | `{테이블명단수}_id` | `user_id`, `order_id` |
| 인덱스 | `ix_{테이블}_{컬럼}` | `ix_users_email` |

### 8.2 마이그레이션 규칙

```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "add orders table"

# 마이그레이션 적용
alembic upgrade head

# 1단계 롤백
alembic downgrade -1
```

- 마이그레이션 파일은 반드시 Git에 커밋합니다.
- 프로덕션 배포 전 마이그레이션을 반드시 테스트하세요.

---

## 9. Git 컨벤션

### 9.1 브랜치 전략

| 브랜치 | 용도 |
|--------|------|
| `main` | 프로덕션 릴리스 |
| `develop` | 개발 통합 |
| `feature/{기능명}` | 기능 개발 |
| `bugfix/{버그명}` | 버그 수정 |
| `hotfix/{긴급수정}` | 긴급 수정 |

### 9.2 커밋 메시지 규칙

```
<type>: <subject>

[body]

[footer]
```

| Type | 설명 |
|------|------|
| `feat` | 새로운 기능 |
| `fix` | 버그 수정 |
| `refactor` | 리팩토링 |
| `docs` | 문서 수정 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드, 설정 등 |

예시:
```
feat: 주문 관리 API 추가

- POST /api/v1/orders - 주문 생성
- GET /api/v1/orders - 주문 목록 조회
- GET /api/v1/orders/{id} - 주문 상세 조회
```

---

## 10. 테스트 표준

### 10.1 테스트 실행

```bash
# 백엔드 테스트
cd backend
pytest                      # 전체 테스트
pytest -v                   # 상세 출력
pytest --cov=app           # 커버리지 측정
pytest tests/test_health.py # 특정 파일만 실행

# 프론트엔드 (추후 설정)
cd frontend
npm run lint               # 린트 검사
npm run type-check         # 타입 체크
```

### 10.2 테스트 규칙

- 커버리지 목표: **80% 이상**
- API 엔드포인트별 최소 1개 이상의 테스트 작성
- 테스트 DB는 인메모리 SQLite 사용 (실제 DB 격리)

---

> **📌 참고**: 이 가이드는 프로젝트 진행에 따라 지속적으로 업데이트됩니다.
