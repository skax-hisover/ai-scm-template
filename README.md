# AI-SCM Template

개발자들이 일관된 코드 품질과 구조를 유지하면서 빠르게 기능을 개발할 수 있도록, 백엔드·프론트엔드·인프라의 **개발 표준과 아키텍처**를 사전에 정의한 템플릿입니다.

---

## 📋 목차

1. [기술 스택](#-기술-스택)
2. [아키텍처 개요](#-아키텍처-개요)
3. [프로젝트 구조](#-프로젝트-구조)
4. [빠른 시작 (Quick Start)](#-빠른-시작-quick-start)
5. [환경 변수](#-환경-변수)
6. [Docker Compose](#-docker-compose)
7. [접속 URL 및 기본 계정](#-접속-url-및-기본-계정)
8. [API 설계 규칙](#-api-설계-규칙)
9. [데이터베이스 규칙](#-데이터베이스-규칙)
10. [Git 컨벤션](#-git-컨벤션)
11. [상세 가이드](#-상세-가이드)

---

## 🛠 기술 스택

| 구분 | 기술 | 버전 |
|------|------|------|
| **백엔드 프레임워크** | FastAPI | ≥ 0.115 |
| **ORM** | SQLAlchemy | ≥ 2.0 |
| **DB 마이그레이션** | Alembic | ≥ 1.14 |
| **비동기 태스크** | Celery + Redis | ≥ 5.4 |
| **인증** | JWT (PyJWT) | ≥ 2.8 |
| **프론트엔드** | Next.js (App Router) + React + TypeScript | ≥ 15.1 |
| **HTTP 클라이언트** | Axios | ≥ 1.7 |
| **CSS** | Tailwind CSS | ≥ 4.0 |
| **데이터베이스** | PostgreSQL | ≥ 16 |
| **캐시 / 메시지 브로커** | Redis | ≥ 7 |
| **패키지 관리 (BE)** | uv | ≥ 0.10 |
| **패키지 관리 (FE)** | npm | ≥ 10 |
| **Python** | Python | ≥ 3.11 |
| **Node.js** | Node.js | ≥ 20 |
| **컨테이너** | Docker + Docker Compose | — |
| **모니터링** | Sentry (선택) | — |

---

## 🏗 아키텍처 개요

```
┌───────────────────────────────────────────────────────────────────┐
│                        클라이언트 (브라우저)                         │
└────────────────────────────┬──────────────────────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │   Frontend (Next.js :3000)  │
              │   - App Router (SSR/CSR)    │
              │   - Axios → API 호출         │
              │   - JWT 토큰 관리            │
              └──────────────┬──────────────┘
                             │ HTTP (REST API)
              ┌──────────────▼──────────────┐
              │   Backend (FastAPI :8000)   │
              │   ┌───────────────────────┐ │
              │   │ API Layer (api/v1/)   │ │ ← 요청/응답, 인증 검증
              │   │         ↓             │ │
              │   │ CRUD Layer (crud/)    │ │ ← 데이터 접근 로직
              │   │         ↓             │ │
              │   │ Model Layer (models/) │ │ ← SQLAlchemy ORM
              │   └───────────────────────┘ │
              │   - JWT 인증 (PyJWT)         │
              │   - 구조화된 로깅 (JSON)      │
              │   - 전역 에러 핸들링          │
              │   - CORS / 미들웨어          │
              └──┬───────────────────────┬──┘
                 │                       │
    ┌────────────▼──────┐    ┌──────────▼────────────┐
    │ PostgreSQL (:5432)│    │   Redis (:6379)       │
    │ - 영속 데이터 저장  │    │   - Celery 브로커      │
    │ - Alembic 마이그   │    │   - 결과 백엔드         │
    └───────────────────┘    └──────────┬────────────┘
                                        │
                             ┌──────────▼────────────┐
                             │   Celery Worker       │
                             │   - 비동기 태스크 처리   │
                             └───────────────────────┘
```

### 핵심 설계 원칙

| 원칙 | 설명 |
|------|------|
| **레이어 분리** | API → CRUD → Model 3계층 아키텍처로 관심사 분리 |
| **환경 변수 기반 설정** | `pydantic-settings`로 타입 안전한 설정 관리, 하드코딩 금지 |
| **JWT 인증** | Access Token + Refresh Token 기반 인증 흐름 |
| **구조화된 로깅** | JSON 형식 로그 → ELK, CloudWatch 등과 연동 가능 |
| **제네릭 CRUD** | `CRUDBase[Model, CreateSchema, UpdateSchema]`를 상속하여 반복 코드 최소화 |
| **Docker 기반 개발** | `docker-compose.yml`로 로컬 환경을 즉시 구성 |

---

## 📁 프로젝트 구조

```
ai-scm-template/
├── .env.example                    # 환경 변수 템플릿
├── .gitignore
├── docker-compose.yml              # Docker Compose (로컬 개발)
├── README.md                       # 본 문서 (프로젝트 개요)
│
├── backend/                        # ─── 백엔드 (FastAPI) ───
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
├── frontend/                       # ─── 프론트엔드 (Next.js) ───
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── postcss.config.mjs
│   └── src/
│       ├── app/                    # Next.js App Router
│       │   ├── layout.tsx          # 루트 레이아웃
│       │   ├── page.tsx            # 루트 페이지 (리다이렉트)
│       │   ├── globals.css         # 전역 스타일 (Tailwind)
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
│       ├── hooks/
│       │   └── useAuth.ts          # 인증 훅
│       └── types/
│           └── index.ts            # 전역 타입 정의
│
└── docs/                           # ─── 문서 ───
    ├── BACKEND_GUIDE.md            # 백엔드 개발 가이드
    └── FRONTEND_GUIDE.md           # 프론트엔드 개발 가이드
```

---

## 🚀 빠른 시작 (Quick Start)

### 사전 요구사항

| 도구 | 용도 | 설치 |
|------|------|------|
| Python ≥ 3.11 | 백엔드 런타임 | [python.org](https://python.org) |
| Node.js ≥ 20 | 프론트엔드 런타임 | [nodejs.org](https://nodejs.org) |
| uv | Python 패키지 관리 | `pip install uv` |
| PostgreSQL ≥ 16 | 데이터베이스 | [postgresql.org](https://postgresql.org) |
| Redis | Celery 브로커 | [redis.io](https://redis.io) |
| Docker (선택) | 컨테이너 실행 | [docker.com](https://docker.com) |

### 방법 A: Docker Compose (권장)

```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일을 환경에 맞게 수정

# 2. 전체 서비스 실행
docker compose up -d

# 3. DB 마이그레이션 & 초기 데이터 (최초 1회)
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.initial_data
```

### 방법 B: 로컬 직접 실행

```bash
# 1. 환경 변수 설정
cp .env.example .env

# 2. 인프라 서비스 (Docker로 DB + Redis만 실행)
docker compose up -d db redis

# 3. 백엔드
cd backend
uv sync                                              # 의존성 설치
source .venv/bin/activate                            # 가상환경 활성화 (Windows: .venv\Scripts\activate)
alembic upgrade head                                 # DB 마이그레이션
python -m app.initial_data                           # 초기 데이터 생성
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # 서버 시작

# 4. Celery 워커 (별도 터미널)
cd backend
celery -A app.tasks.celery_app worker --loglevel=info

# 5. 프론트엔드 (별도 터미널)
cd frontend
npm install                                          # 의존성 설치
npm run dev                                          # 개발 서버 시작
```

---

## 🔐 환경 변수

프로젝트 루트의 `.env.example`을 `.env`로 복사한 후 환경에 맞게 수정하세요.

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `PROJECT_NAME` | 프로젝트 이름 | `AI-SCM` |
| `ENVIRONMENT` | 환경 (`local` / `staging` / `production`) | `local` |
| `SECRET_KEY` | JWT 서명 키 (**반드시 변경**) | `changethis` |
| `BACKEND_HOST` | 백엔드 URL | `http://localhost:8000` |
| `BACKEND_CORS_ORIGINS` | 허용 CORS 오리진 (쉼표 구분) | `http://localhost:3000,...` |
| `FRONTEND_HOST` | 프론트엔드 URL | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | 프론트엔드에서 사용할 API URL | `http://localhost:8000` |
| `POSTGRES_*` | PostgreSQL 접속 정보 | `localhost:5432` |
| `REDIS_*` | Redis 접속 정보 | `localhost:6379` |
| `CELERY_*` | Celery 브로커/백엔드 URL | `redis://localhost:6379/0,1` |
| `FIRST_SUPERUSER` | 초기 관리자 이메일 | `admin@ai-scm.com` |
| `FIRST_SUPERUSER_PASSWORD` | 초기 관리자 비밀번호 (**반드시 변경**) | `changethis` |
| `LOG_LEVEL` | 로그 레벨 | `INFO` |
| `SENTRY_DSN` | Sentry DSN (선택) | — |

> ⚠️ `SECRET_KEY`, `POSTGRES_PASSWORD`, `FIRST_SUPERUSER_PASSWORD`는 `local` 환경이 아닌 경우 반드시 변경해야 합니다. 기본값(`changethis`) 사용 시 에러가 발생합니다.

### 환경 변수 관리 규칙

- 모든 설정은 `backend/app/core/config.py`의 `Settings` 클래스에 정의
- **하드코딩 금지**, 반드시 환경 변수 사용
- 새로운 환경 변수 추가 시 `.env.example`에도 반드시 반영

---

## 🐳 Docker Compose

`docker-compose.yml`에 정의된 서비스:

| 서비스 | 이미지 | 포트 | 설명 |
|--------|--------|------|------|
| `db` | postgres:16 | 5432 | PostgreSQL 데이터베이스 |
| `redis` | redis:7-alpine | 6379 | Redis (Celery 브로커) |
| `backend` | 커스텀 빌드 | 8000 | FastAPI 백엔드 |
| `celery-worker` | 커스텀 빌드 | — | Celery 비동기 워커 |
| `frontend` | 커스텀 빌드 | 3000 | Next.js 프론트엔드 |
| `pgadmin` | dpage/pgadmin4 | 5050 | DB 관리 도구 (선택) |

```bash
# 사용 예시
docker compose up -d              # 전체 서비스 시작
docker compose up -d db redis     # DB + Redis만 시작
docker compose logs -f backend    # 백엔드 로그 확인
docker compose down -v            # 전체 중지 + 볼륨 삭제
```

---

## 🌐 접속 URL 및 기본 계정

### 접속 URL

| 서비스 | URL |
|--------|-----|
| 프론트엔드 | http://localhost:3000 |
| 백엔드 API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| pgAdmin | http://localhost:5050 |

### 기본 관리자 계정

| 항목 | 값 |
|------|-----|
| 이메일 | `admin@ai-scm.com` |
| 비밀번호 | `changethis` |

---

## 📐 API 설계 규칙

### URL 규칙

| 규칙 | 예시 |
|------|------|
| 기본 접두사 | `/api/v1` |
| 리소스명은 **복수형** | `/api/v1/items` |
| 하이픈 사용 금지 (snake_case) | `/api/v1/order_items` ✅ |
| 동사 사용 금지 | `GET /api/v1/items` ✅ |
| ID는 경로 파라미터 | `/api/v1/items/{item_id}` |

### HTTP 메서드

| 메서드 | 용도 | 응답 코드 |
|--------|------|-----------|
| GET | 조회 | 200 |
| POST | 생성 | 201 |
| PUT | 전체 수정 | 200 |
| PATCH | 부분 수정 | 200 |
| DELETE | 삭제 | 200 |

### 응답 형식

```json
// 단건 응답
{
  "id": "uuid",
  "title": "아이템",
  "created_at": "2026-01-01T00:00:00Z"
}

// 목록 응답 (페이지네이션)
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

## 🗄 데이터베이스 규칙

### 네이밍 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| 테이블명 | snake_case **복수형** | `users`, `order_items` |
| 컬럼명 | snake_case | `created_at`, `owner_id` |
| PK | `id` (UUID) | 모든 테이블 공통 |
| FK | `{테이블명_단수}_id` | `user_id`, `order_id` |
| 인덱스 | `ix_{테이블}_{컬럼}` | `ix_users_email` |

### 마이그레이션

```bash
cd backend

# 마이그레이션 생성 (모델 변경 후)
alembic revision --autogenerate -m "add orders table"

# 마이그레이션 적용
alembic upgrade head

# 1단계 롤백
alembic downgrade -1

# 마이그레이션 이력 확인
alembic history
```

> - 마이그레이션 파일은 반드시 Git에 커밋합니다.
> - 프로덕션 배포 전 마이그레이션을 반드시 테스트하세요.

---

## 📝 Git 컨벤션

### 브랜치 전략

| 브랜치 | 용도 |
|--------|------|
| `main` | 프로덕션 릴리스 |
| `develop` | 개발 통합 |
| `feature/{기능명}` | 기능 개발 |
| `bugfix/{버그명}` | 버그 수정 |
| `hotfix/{긴급수정}` | 긴급 수정 |

### 커밋 메시지 규칙

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

## 📚 상세 가이드

| 문서 | 설명 |
|------|------|
| **[백엔드 개발 가이드](docs/BACKEND_GUIDE.md)** | FastAPI 레이어 아키텍처, 기능 추가 절차, 코딩 규칙, 테스트, 빌드/배포 방법 |
| **[프론트엔드 개발 가이드](docs/FRONTEND_GUIDE.md)** | Next.js App Router, 컴포넌트 구조, API 호출 규칙, 인증 흐름, 빌드/배포 방법 |

---

> **📌 참고**: 이 가이드는 프로젝트 진행에 따라 지속적으로 업데이트됩니다.
