# 프론트엔드 개발 가이드

> Next.js (App Router) 기반 프론트엔드의 개발 환경, 개발 표준, 기능 추가 가이드, 빌드·실행·배포 방법을 정의합니다.

---

## 📋 목차

1. [개발 환경 설정](#1-개발-환경-설정)
2. [디렉터리 구조 및 규칙](#2-디렉터리-구조-및-규칙)
3. [새로운 기능 추가 절차](#3-새로운-기능-추가-절차)
4. [코딩 규칙](#4-코딩-규칙)
5. [핵심 모듈 가이드](#5-핵심-모듈-가이드)
6. [테스트 및 검증](#6-테스트-및-검증)
7. [빌드, 실행 및 종료](#7-빌드-실행-및-종료)
8. [배포](#8-배포)

---

## 1. 개발 환경 설정

### 1.1 사전 요구사항

아래 도구가 설치되어 있어야 합니다. 터미널에서 명령어를 실행하여 확인하세요.

| 도구 | 버전 | 설치 확인 | 설치 방법 |
|------|------|-----------|-----------|
| Node.js | ≥ 20 | `node --version` | [nodejs.org](https://nodejs.org) |
| npm | ≥ 10 | `npm --version` | Node.js에 포함 |

> 💡 Node.js를 설치하면 npm이 함께 설치됩니다.

### 1.2 초기 설정 (Step by Step)

> 이 절차는 **처음 프로젝트를 세팅할 때 1회만** 수행합니다.

**Step 1.** 프로젝트 루트에서 환경 변수 파일을 생성합니다. (아직 없는 경우)

```bash
cd ai-scm-template

# macOS / Linux
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

> `.env` 파일의 `NEXT_PUBLIC_API_URL`이 백엔드 주소(기본값: `http://localhost:8000`)와 일치하는지 확인하세요.

**Step 2.** `frontend` 폴더로 이동하여 Node.js 의존성을 설치합니다.

```bash
cd frontend
npm install
```

> `npm install`은 `package.json`에 정의된 모든 패키지를 `node_modules/` 폴더에 설치합니다.
> 처음 실행 시 몇 분이 소요될 수 있습니다.

### 1.3 환경 변수

프론트엔드에서 사용하는 환경 변수:

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `NEXT_PUBLIC_API_URL` | 백엔드 API URL | `http://localhost:8000` |

> `NEXT_PUBLIC_` 접두사가 붙은 변수만 클라이언트 번들에 포함됩니다. 민감한 정보는 이 접두사를 사용하지 마세요.

### 1.4 의존성 관리

| 작업 | 명령어 |
|------|--------|
| 전체 의존성 설치 | `npm install` |
| 패키지 추가 | `npm install <패키지명>` |
| 개발 의존성 추가 | `npm install -D <패키지명>` |
| 패키지 제거 | `npm uninstall <패키지명>` |

### 1.5 주요 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `next` | ≥ 15.1 | React 프레임워크 (App Router) |
| `react` / `react-dom` | ≥ 19.0 | UI 라이브러리 |
| `axios` | ≥ 1.7 | HTTP 클라이언트 |
| `tailwindcss` | ≥ 4.0 | 유틸리티 CSS |
| `lucide-react` | ≥ 0.460 | 아이콘 |
| `clsx` + `tailwind-merge` | — | 조건부 클래스 유틸리티 |
| `typescript` | ≥ 5.7 | 타입 시스템 |
| `eslint` + `eslint-config-next` | — | 코드 품질 검사 |

---

## 2. 디렉터리 구조 및 규칙

```
frontend/src/
├── app/                        # Next.js App Router (페이지)
│   ├── layout.tsx              # 루트 레이아웃
│   ├── page.tsx                # 루트 페이지 (리다이렉트)
│   ├── globals.css             # 전역 스타일 (Tailwind)
│   ├── login/
│   │   └── page.tsx            # 로그인 페이지
│   └── dashboard/              # 대시보드 (인증 필요)
│       ├── layout.tsx          # 대시보드 레이아웃 (사이드바)
│       ├── page.tsx            # 대시보드 메인
│       └── items/
│           └── page.tsx        # 아이템 관리
│
├── components/                 # 재사용 컴포넌트
│   └── ui/                     # 공통 UI 컴포넌트
│       ├── Button.tsx
│       └── Input.tsx
│
├── lib/                        # 라이브러리 / 유틸리티
│   ├── api/                    # API 호출 함수
│   │   ├── client.ts           # Axios 인스턴스 (인터셉터)
│   │   ├── auth.ts             # 인증 API
│   │   └── items.ts            # 아이템 API
│   └── auth/
│       └── token.ts            # JWT 토큰 관리
│
├── hooks/                      # 커스텀 훅
│   └── useAuth.ts              # 인증 훅
│
└── types/                      # 전역 TypeScript 타입
    └── index.ts
```

### 디렉터리별 역할

| 경로 | 용도 | 규칙 |
|------|------|------|
| `src/app/` | 페이지 (Next.js App Router) | 파일 기반 라우팅, `page.tsx`가 라우트 |
| `src/components/ui/` | 공통 UI 컴포넌트 (Button, Input 등) | 비즈니스 로직 없이 순수 UI만 |
| `src/components/features/` | 기능별 컴포넌트 (추후 추가) | 특정 도메인 로직 포함 가능 |
| `src/lib/api/` | API 호출 함수 | 반드시 `apiClient` 인스턴스 사용 |
| `src/lib/auth/` | 인증 관련 유틸리티 | 토큰 저장/조회/삭제 |
| `src/hooks/` | 커스텀 훅 | `use` 접두사, 재사용 가능한 상태 로직 |
| `src/types/` | 전역 TypeScript 타입 정의 | 여러 곳에서 공유되는 타입만 |

---

## 3. 새로운 기능 추가 절차

새로운 페이지(예: 주문 관리)를 추가하는 전체 절차입니다.

### Step 1. API 함수 작성 (`lib/api/orders.ts`)

```typescript
/**
 * 주문 관련 API 함수.
 */
import apiClient from "./client";

export interface Order {
  id: string;
  title: string;
  quantity: number;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface OrderCreate {
  title: string;
  quantity?: number;
}

/** 주문 목록 조회 */
export async function getOrdersApi(skip = 0, limit = 20): Promise<Order[]> {
  const response = await apiClient.get<Order[]>("/orders", {
    params: { skip, limit },
  });
  return response.data;
}

/** 주문 생성 */
export async function createOrderApi(data: OrderCreate): Promise<Order> {
  const response = await apiClient.post<Order>("/orders", data);
  return response.data;
}

/** 주문 상세 조회 */
export async function getOrderApi(id: string): Promise<Order> {
  const response = await apiClient.get<Order>(`/orders/${id}`);
  return response.data;
}
```

### Step 2. 페이지 생성 (`app/dashboard/orders/page.tsx`)

```tsx
"use client";

import { useEffect, useState } from "react";
import { getOrdersApi, type Order } from "@/lib/api/orders";

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchOrders() {
      try {
        const data = await getOrdersApi();
        setOrders(data);
      } catch (error) {
        console.error("주문 목록 조회 실패:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchOrders();
  }, []);

  if (loading) return <div>로딩중...</div>;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">주문 관리</h1>
      {/* 주문 목록 렌더링 */}
    </div>
  );
}
```

### Step 3. 사이드바에 메뉴 추가 (`app/dashboard/layout.tsx`)

```tsx
{/* 기존 메뉴 아래에 추가 */}
<Link
  href="/dashboard/orders"
  className="block rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-gray-100"
>
  📋 주문 관리
</Link>
```

### Step 4. 타입 공유 (필요한 경우)

여러 곳에서 공유되는 타입은 `types/index.ts`에 추가:

```typescript
/** 주문 상태 */
export type OrderStatus = "pending" | "confirmed" | "shipped" | "delivered";
```

---

## 4. 코딩 규칙

### 4.1 코드 품질 도구

| 도구 | 역할 | 설정 파일 |
|------|------|-----------|
| **ESLint** | Linter (코드 품질) | `eslint-config-next` 사용 |
| **TypeScript** | 타입 검사 (strict 모드) | `tsconfig.json` |
| **Tailwind CSS** | 유틸리티 CSS | `postcss.config.mjs` |

### 4.2 검사 실행

```bash
cd frontend

# ESLint 린트 검사
npm run lint

# TypeScript 타입 체크
npm run type-check
```

### 4.3 TypeScript 규칙

- **strict 모드** 활성화 (`tsconfig.json` → `"strict": true`)
- `any` 타입 사용 최소화
- API 응답에 반드시 타입 정의

```typescript
// ✅ Good
const response = await apiClient.get<Order[]>("/orders");

// ❌ Bad
const response = await apiClient.get("/orders");  // 타입 없음
```

### 4.4 네이밍 컨벤션

| 대상 | 규칙 | 예시 |
|------|------|------|
| 변수 / 함수 | `camelCase` | `getOrders`, `isLoading` |
| 컴포넌트 | `PascalCase` | `OrderList`, `Button` |
| 타입 / 인터페이스 | `PascalCase` | `Order`, `ApiError` |
| 상수 | `UPPER_SNAKE_CASE` | `API_BASE_URL` |
| 파일명 (컴포넌트) | `PascalCase` | `Button.tsx`, `OrderList.tsx` |
| 파일명 (유틸/훅) | `camelCase` | `useAuth.ts`, `token.ts` |
| 파일명 (페이지) | `page.tsx` (Next.js 규칙) | `app/orders/page.tsx` |

### 4.5 컴포넌트 규칙

- **함수형 컴포넌트** + Hooks 사용 (클래스 컴포넌트 사용 금지)
- **상태 관리**: React Hooks (`useState`, `useEffect`, `useCallback` 등)
- 필요 시 **Context API** 활용
- 클라이언트 컴포넌트에는 파일 최상단에 `"use client"` 선언

```tsx
"use client";

import { useState } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>Count: {count}</button>;
}
```

### 4.6 스타일 규칙

- **Tailwind CSS** 유틸리티 클래스 사용
- 인라인 `style` 사용 최소화
- 조건부 클래스: `clsx` + `tailwind-merge` 활용

```tsx
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// 유틸리티 함수
function cn(...inputs: (string | undefined | false)[]) {
  return twMerge(clsx(inputs));
}

// 사용
<button className={cn("rounded px-4 py-2", isActive && "bg-blue-600 text-white")}>
  버튼
</button>
```

### 4.7 Import 경로

- **절대 경로** 사용 (`@/` 접두사 → `src/` 매핑)
- `tsconfig.json`의 `paths` 설정으로 동작

```typescript
// ✅ Good - 절대 경로
import apiClient from "@/lib/api/client";
import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/ui/Button";

// ❌ Bad - 상대 경로
import apiClient from "../../../lib/api/client";
```

---

## 5. 핵심 모듈 가이드

### 5.1 API 클라이언트 (`lib/api/client.ts`)

모든 API 호출은 반드시 이 클라이언트 인스턴스를 통해 수행합니다.

#### 주요 기능

| 기능 | 설명 |
|------|------|
| Base URL | `NEXT_PUBLIC_API_URL` + `/api/v1` 자동 설정 |
| 타임아웃 | 30초 |
| 토큰 자동 주입 | 요청 인터셉터에서 `Authorization: Bearer <token>` 자동 추가 |
| 자동 토큰 갱신 | 401 응답 시 Refresh Token으로 재발급 시도 |
| 자동 로그아웃 | 토큰 갱신 실패 시 `/login`으로 리다이렉트 |

#### 사용법

```typescript
// ✅ Good - apiClient 인스턴스 사용
import apiClient from "@/lib/api/client";

const response = await apiClient.get<Order[]>("/orders");
const newOrder = await apiClient.post<Order>("/orders", { title: "테스트" });

// ❌ Bad - axios 직접 사용
import axios from "axios";
const response = await axios.get("http://localhost:8000/api/v1/orders");
```

### 5.2 JWT 토큰 관리 (`lib/auth/token.ts`)

| 함수 | 설명 |
|------|------|
| `getAccessToken()` | Access Token 조회 |
| `getRefreshToken()` | Refresh Token 조회 |
| `setTokens(access, refresh)` | 토큰 저장 |
| `removeTokens()` | 토큰 삭제 (로그아웃) |
| `isAuthenticated()` | 로그인 여부 확인 |

- 토큰은 `localStorage`에 저장
- SSR 환경 안전: `typeof window === "undefined"` 체크 포함
- 프로덕션에서는 `httpOnly 쿠키` 방식으로 전환 권장

### 5.3 인증 훅 (`hooks/useAuth.ts`)

컴포넌트에서 인증 관련 로직을 사용할 때 이 훅을 활용합니다.

```tsx
"use client";

import { useAuth } from "@/hooks/useAuth";

export default function ProfilePage() {
  const { user, loading, isLoggedIn, login, logout } = useAuth();

  if (loading) return <div>로딩중...</div>;
  if (!isLoggedIn) return <div>로그인이 필요합니다</div>;

  return (
    <div>
      <p>환영합니다, {user?.full_name}님!</p>
      <button onClick={logout}>로그아웃</button>
    </div>
  );
}
```

| 반환값 | 타입 | 설명 |
|--------|------|------|
| `user` | `UserResponse \| null` | 현재 로그인된 사용자 정보 |
| `loading` | `boolean` | 사용자 정보 로딩 중 여부 |
| `isLoggedIn` | `boolean` | 로그인 여부 |
| `login(email, password)` | `Promise<void>` | 로그인 (성공 시 대시보드로 이동) |
| `logout()` | `void` | 로그아웃 (토큰 삭제 + 로그인 페이지 이동) |

### 5.4 인증 흐름

```
1. 로그인
   POST /api/v1/auth/login/json { email, password }
       ↓
   { access_token, refresh_token } → localStorage 저장
       ↓
   /dashboard로 리다이렉트

2. 인증된 API 호출
   apiClient → 요청 인터셉터가 Authorization 헤더 자동 주입
       ↓
   백엔드 → JWT 검증 → 응답

3. 토큰 만료 시 (401 응답)
   응답 인터셉터 → POST /api/v1/auth/refresh { refresh_token }
       ↓
   성공: 새 토큰으로 재시도
   실패: removeTokens() → /login으로 리다이렉트
```

### 5.5 대시보드 레이아웃 (`app/dashboard/layout.tsx`)

- **인증이 필요한 페이지**는 반드시 `app/dashboard/` 하위에 배치
- 레이아웃에서 `isAuthenticated()` 확인 → 미인증 시 `/login`으로 리다이렉트
- 사이드바, 헤더 등 공통 UI를 레이아웃에서 관리

새 메뉴 추가 위치:

```tsx
{/* ─── 새로운 메뉴 추가 위치 ─── */}
<Link href="/dashboard/orders" className="...">📋 주문 관리</Link>
```

### 5.6 Next.js API Proxy (`next.config.ts`)

`/api/*` 요청은 Next.js의 `rewrites`를 통해 백엔드로 프록시됩니다. 이로써 CORS 문제 없이 API 호출이 가능합니다.

```typescript
// next.config.ts
async rewrites() {
  return [
    {
      source: "/api/:path*",
      destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
    },
  ];
}
```

### 5.7 전역 타입 (`types/index.ts`)

여러 곳에서 공유되는 타입만 이 파일에 정의합니다. API 응답 타입은 해당 API 모듈(`lib/api/`)에 정의합니다.

```typescript
// 공통 타입 예시
export interface ApiError { detail: string; }
export interface PaginatedResponse<T> { data: T[]; total: number; page: number; size: number; }
export interface MessageResponse { message: string; }
```

---

## 6. 테스트 및 검증

### 6.1 코드 검증

```bash
cd frontend

# ESLint 린트 검사
npm run lint

# TypeScript 타입 체크
npm run type-check
```

### 6.2 검증 규칙

- 모든 코드 변경 시 `npm run lint` 및 `npm run type-check` 통과 필수
- ESLint 경고(warning)도 가능한 한 해결
- `@ts-ignore` 사용 금지 (불가피한 경우 `@ts-expect-error` 사용 + 사유 주석)

### 6.3 테스트 프레임워크 (추후 도입)

프로젝트 규모가 커지면 다음 도구를 도입하세요:

| 도구 | 용도 |
|------|------|
| Jest + React Testing Library | 컴포넌트 단위 테스트 |
| Playwright 또는 Cypress | E2E 테스트 |
| Storybook | 컴포넌트 문서화 및 시각적 테스트 |

---

## 7. 빌드, 실행 및 종료

### 7.1 개발 서버 실행

> 개발 서버는 코드를 수정하면 **자동으로 화면이 갱신**(Hot Reload)됩니다.
> `frontend/` 폴더에서 실행하세요.

```bash
cd frontend

# 개발 서버 시작
npm run dev
```

> ✅ `Ready in Xs` 메시지가 나타나면 정상입니다.
> 브라우저에서 http://localhost:3000 에 접속하여 화면을 확인할 수 있습니다.

### 7.2 개발 서버 종료

```bash
# 실행 중인 터미널에서 Ctrl+C를 눌러 서버를 종료합니다.
```

> 💡 `Ctrl+C`: 키보드에서 `Ctrl` 키를 누른 채 `C` 키를 누릅니다. 현재 실행 중인 프로그램을 중단합니다.

### 7.3 프로덕션 빌드

> 프로덕션 빌드는 코드를 최적화하여 실제 운영 환경에서 사용할 결과물을 생성합니다.

```bash
cd frontend

# 프로덕션 빌드 (최적화된 결과물 생성)
npm run build

# 빌드 결과 확인 (.next/ 디렉터리 생성)
# 빌드된 앱 실행
npm run start

# 종료: Ctrl+C 입력
```

> 빌드된 앱은 http://localhost:3000 에서 확인할 수 있습니다.

### 7.4 npm scripts 요약

| 스크립트 | 명령어 | 설명 |
|----------|--------|------|
| `dev` | `next dev` | 개발 서버 (Hot Reload) |
| `build` | `next build` | 프로덕션 빌드 |
| `start` | `next start` | 프로덕션 서버 실행 |
| `lint` | `next lint` | ESLint 검사 |
| `type-check` | `tsc --noEmit` | TypeScript 타입 검사 |

### 7.5 Docker 빌드

> Docker 이미지를 직접 빌드하는 방법입니다. **프로젝트 루트 폴더**에서 실행하세요.

프론트엔드 Dockerfile은 **3단계 멀티스테이지 빌드**를 사용합니다:

| 스테이지 | 베이스 이미지 | 역할 |
|----------|--------------|------|
| `deps` | `node:20-alpine` | 의존성 설치 |
| `builder` | `node:20-alpine` | Next.js 빌드 |
| `runner` | `node:20-alpine` | 프로덕션 실행 (최소 이미지) |

```bash
# 프론트엔드 이미지 빌드
docker build -f frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_API_URL=http://api.example.com \
  -t ai-scm-frontend .

# 빌드된 이미지 실행
docker run -p 3000:3000 ai-scm-frontend

# 종료: 다른 터미널에서
docker ps                              # 실행 중인 컨테이너 ID 확인
docker stop <CONTAINER_ID>             # 컨테이너 종료
```

> ⚠️ `NEXT_PUBLIC_API_URL`은 **빌드 시점**에 결정됩니다 (`--build-arg`로 전달). 런타임에 변경할 수 없습니다.

### 7.6 Docker Compose

```bash
# 프론트엔드만 빌드 및 실행
docker compose up -d --build frontend

# 로그 확인
docker compose logs -f frontend

# 종료
docker compose down
```

---

## 8. 배포

### 8.1 배포 전 체크리스트

- [ ] `npm run lint` 통과
- [ ] `npm run type-check` 통과
- [ ] `npm run build` 성공
- [ ] `NEXT_PUBLIC_API_URL` 프로덕션 API URL로 설정
- [ ] 불필요한 `console.log` 제거
- [ ] 이미지/정적 파일 최적화

### 8.2 빌드 아티팩트

`npm run build` 실행 시 `.next/` 디렉터리에 빌드 결과가 생성됩니다:

```
.next/
├── standalone/     # 독립 실행 가능한 서버 (node server.js)
├── static/         # 정적 파일 (JS, CSS, 이미지)
└── server/         # 서버 사이드 렌더링 코드
```

### 8.3 Docker 기반 배포

```bash
# 프로덕션 이미지 빌드
docker build -f frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_API_URL=https://api.production.com \
  -t ai-scm-frontend:latest .

# 레지스트리 푸시
docker tag ai-scm-frontend:latest <registry>/ai-scm-frontend:latest
docker push <registry>/ai-scm-frontend:latest
```

### 8.4 정적 호스팅 (Vercel, Netlify 등)

Next.js는 Vercel에 최적화되어 있습니다:

1. GitHub 리포지토리 연결
2. 환경 변수 설정: `NEXT_PUBLIC_API_URL`
3. 빌드 명령어: `cd frontend && npm run build`
4. 출력 디렉터리: `frontend/.next`

### 8.5 환경별 API URL 설정

| 환경 | `NEXT_PUBLIC_API_URL` |
|------|----------------------|
| 로컬 개발 | `http://localhost:8000` |
| 스테이징 | `https://api-staging.example.com` |
| 프로덕션 | `https://api.example.com` |

---

> **📌 참고**: 이 가이드는 프로젝트 진행에 따라 지속적으로 업데이트됩니다. 문의 사항이 있으면 팀 채널에서 논의해주세요.
>
> ← [README.md (프로젝트 개요)](../README.md)로 돌아가기
