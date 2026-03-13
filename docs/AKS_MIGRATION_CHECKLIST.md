# AKS 전환 체크리스트 (파일 단위)

> 대상: 현재 `docker-compose` 기반 로컬/개발 운영에서 Azure AKS 기반 운영으로 전환  
> 목적: 이 레포 기준으로 "어떤 파일을 무엇으로 바꿔야 하는지"를 빠르게 점검
> v1 점검 기준: **코드/설정 파일에서 확인 가능한 사실만 완료 처리**, Azure/GitHub 실제 리소스 상태는 확인 필요로 유지

---

## 1) 전환 범위 요약

- 애플리케이션 코드(`backend/app`, `frontend/src`)는 대규모 수정이 필요하지 않음
- 핵심 수정 대상은 배포/인프라 관련 파일
- 이 레포는 이미 AKS/CD 뼈대(`k8s/`, `.github/workflows/deploy-*.yml`)가 있으므로 보완 중심으로 진행

---

## 2) 사전 준비 (Azure/GitHub)

### [ ] Azure 리소스 준비
- [ ] AKS 클러스터(dev/prod) 준비
- [ ] ACR 준비 (예: `myacr.azurecr.io`)
- [ ] (권장) Azure Database for PostgreSQL / Azure Cache for Redis 준비
- [ ] 도메인 및 TLS 인증서 전략 확정 (Traefik + cert-manager 또는 다른 ingress)

### [ ] GitHub Secrets / Variables 등록
- [ ] `AZURE_CREDENTIALS`
- [ ] `ACR_LOGIN_SERVER`
- [ ] `ACR_USERNAME`
- [ ] `ACR_PASSWORD`
- [ ] `AKS_RESOURCE_GROUP`
- [ ] `AKS_CLUSTER_NAME_DEV`
- [ ] `AKS_CLUSTER_NAME_PROD`
- [ ] `K8S_NAMESPACE_DEV`
- [ ] `K8S_NAMESPACE_PROD`
- [ ] `DEV_API_URL`
- [ ] `PROD_API_URL`
- [ ] (선택) `SLACK_WEBHOOK_URL`

---

## 3) 파일별 체크리스트

### A. CI/CD

#### `.github/workflows/deploy-dev.yml`
- [ ] `Secrets/Variables` 이름이 실제 GitHub 설정과 일치하는지 확인 *(외부 확인 필요)*
- [ ] `k8s/overlays/dev` 배포가 현재 클러스터/네임스페이스로 적용되는지 확인 *(외부 확인 필요)*
- [ ] `vars.DEV_API_URL`가 실제 dev 백엔드 도메인으로 설정되었는지 확인 *(외부 확인 필요)*
- [x] `deploy` job 조건(`use-acr == true`)이 운영 의도와 맞는지 확인 *(현재 워크플로우에 조건 존재)*
- [ ] (필요 시) 배포 후 smoke test 단계 추가 (`/api/v1/health` 호출)

#### `.github/workflows/deploy-prod.yml`
- [ ] `AKS_CLUSTER_NAME_PROD`, `K8S_NAMESPACE_PROD`, `PROD_API_URL` 값 검증 *(외부 확인 필요)*
- [ ] `environment: production` 수동 승인 정책 사용 여부 결정 후 반영 *(현재 주석 처리됨)*
- [x] Trivy 차단 조건(`CRITICAL`)이 보안 정책과 일치하는지 확인 *(워크플로우에 `exit-code: 1`, `severity: CRITICAL` 적용)*
- [ ] 롤백 전략(이전 이미지 태그 재배포) 운영 절차 문서화

#### `.github/workflows/ci.yml`
- [x] 현재 CI가 AKS 전환 후에도 동일하게 유효한지 확인 *(빌드/린트/테스트 파이프라인 분리 구조 확인)*
- [ ] 필요 시 통합 테스트 단계(실제 외부 DB/Redis 연결 테스트) 분리

---

### B. Kubernetes 매니페스트

#### `k8s/base/backend-deployment.yaml`
- [ ] `envFrom` 참조(`backend-config`, `backend-secret`)가 실제 리소스로 생성되는지 확인 *(`backend-config`는 overlays에 존재, `backend-secret`은 매니페스트 확인 필요)*
- [x] readiness/liveness 경로(`/api/v1/health`)와 실제 API 스펙 일치 확인
- [ ] `resources.requests/limits`를 실제 트래픽 기준으로 재조정
- [ ] (권장) `startupProbe` 추가 검토

#### `k8s/base/frontend-deployment.yaml`
- [x] 프론트엔드 readiness/liveness 프로브가 설정되어 있음 (`/`)
- [ ] 프론트엔드 readiness/liveness 기준 검토 (`/` 대신 헬스 엔드포인트 고려)
- [ ] 리소스 제한 값(100m/128Mi 등) 부하 테스트 기반으로 튜닝
- [x] 환경변수(`NODE_ENV`)가 기본 적용되어 있음
- [ ] 환경변수(`NODE_ENV`) 외 런타임 필요값이 있는지 점검

#### `k8s/base/backend-service.yaml`
- [x] 서비스 포트/타겟포트가 backend 컨테이너와 일치하는지 확인
- [x] 내부 통신 전용(ClusterIP) 정책 유지 여부 확인

#### `k8s/base/frontend-service.yaml`
- [x] 서비스 포트/타겟포트 점검
- [x] ingress 라우팅과 프론트엔드 서비스 경로 일치 확인

#### `k8s/base/traefik-ingressroute.yaml`
- [ ] 기본 도메인(`ai-scm.example.com`)을 실제 도메인으로 대체(overlay patch 포함) *(현재 예시 도메인)*
- [ ] TLS secretName 운영값 확정 (`ai-scm-*-tls`) *(현재 예시 값)*
- [ ] Traefik CRD 설치/버전 호환 확인 *(외부 확인 필요)*
- [ ] (필요 시) NGINX Ingress 사용 조직이라면 IngressRoute -> Ingress 전환

#### `k8s/base/traefik-middleware.yaml`
- [x] Rate limit 미들웨어 값이 정의되어 있음 (`average`, `burst`, `period`)
- [ ] CORS 허용 도메인 목록을 환경별 도메인으로 제한 *(base는 `*`, prod overlay에서 일부 제한)*
- [ ] Rate limit 값(초당/버스트)이 서비스 정책과 일치하는지 확인

#### `k8s/base/kustomization.yaml`
- [ ] base에서 관리하는 리소스 누락 여부 점검 (Secret, ConfigMap, HPA 등) *(현재 base에 Secret/ConfigMap/HPA 미포함)*

#### `k8s/overlays/dev/kustomization.yaml`
- [ ] `images.newName`의 `PLACEHOLDER.azurecr.io` 실제 ACR로 교체 확인 *(현재 placeholder 상태)*
- [ ] dev 도메인(`dev.ai-scm.example.com`) 실도메인 반영 *(현재 예시 도메인)*
- [ ] `backend-config`의 DB/Redis 호스트가 실제 dev 인프라와 일치하는지 확인
- [ ] `ENVIRONMENT=development`가 앱 설정 정책과 맞는지 확인 (`local/staging/production` 사용 여부) *(현재 코드 enum과 불일치 가능성 높음)*

#### `k8s/overlays/prod/kustomization.yaml`
- [ ] `images.newName` ACR 반영 확인 *(현재 placeholder 상태)*
- [ ] prod 도메인/TLS secretName 확인 *(현재 예시 값)*
- [ ] `backend-config`의 `POSTGRES_*`/`FRONTEND_HOST` 실운영 값 반영
- [ ] replica/리소스 설정이 SLO 기준에 맞는지 검증

---

### C. 앱 설정/시크릿 주입

#### `backend/app/core/config.py`
- [x] 운영환경 기본 시크릿 값 차단 로직이 구현되어 있음
- [ ] 운영환경에서 `SECRET_KEY`, `POSTGRES_PASSWORD`, `FIRST_SUPERUSER_PASSWORD`를 K8S Secret로 주입하는지 확인 *(외부/매니페스트 확인 필요)*
- [ ] `ENVIRONMENT` 값 정책 통일 (`staging` 또는 `production`)
- [ ] CORS(`BACKEND_CORS_ORIGINS`, `FRONTEND_HOST`)가 실도메인과 일치하는지 확인
- [ ] 관리형 DB 사용 시 `POSTGRES_SERVER/PORT/DB` 값을 올바르게 반영

#### `frontend/next.config.ts`
- [x] `NEXT_PUBLIC_API_URL`가 환경(dev/prod)별 배포 파이프라인 변수와 연계 가능한 구조
- [x] rewrite 프록시 경로(`/api/:path*`)가 ingress 라우팅과 충돌 없는 기본 구조
- [ ] `NEXT_PUBLIC_API_URL` 실제 환경값(dev/prod) 운영 반영 확인 *(외부 확인 필요)*

---

### D. 컨테이너/로컬 스크립트

#### `backend/Dockerfile`
- [ ] 현재 런타임 옵션(`workers=4`)이 AKS 리소스/CPU와 과도하지 않은지 검토
- [ ] healthcheck(이미지 레벨)가 필요하면 추가 검토

#### `frontend/Dockerfile`
- [x] `NEXT_PUBLIC_API_URL` 빌드 인자 주입 구조 존재
- [x] standalone 런타임(server.js) 방식 적용

#### `docker-compose.yml`
- [x] 로컬 개발용 Compose 구조가 이미 분리되어 있음
- [ ] 운영 문서에서 Compose를 운영 배포 수단으로 오해하지 않도록 구분 문구 추가

---

### E. 문서

#### `README.md`
- [x] 프로젝트 구조/워크플로우 기준으로 AKS 관련 파일은 문서에 반영됨
- [ ] "로컬 실행(Compose)"과 "AKS 배포"를 명확히 분리 설명
- [ ] AKS 필수 Secrets/Variables 표 추가
- [ ] 장애 대응(롤백/로그 확인) 기본 절차 추가

#### `docs/BACKEND_GUIDE.md`
- [ ] 로컬 실행 절차와 AKS 배포 시 환경변수 주입 차이를 명시
- [ ] DB/Redis를 관리형 서비스로 바꿀 때의 설정 변경 가이드 추가

#### `docs/FRONTEND_GUIDE.md`
- [x] `NEXT_PUBLIC_API_URL`의 환경별(로컬/dev/prod) 관리 방법 명시
- [x] 빌드 시점 변수와 런타임 변수의 차이 재강조

---

## 4) 운영 안정화 체크 (권장)

- [ ] HPA 적용 (backend/frontend)
- [ ] PodDisruptionBudget 적용
- [ ] Secret 관리 고도화 (예: External Secrets, Key Vault 연계)
- [ ] 관측성 구성 (Azure Monitor + Log Analytics + Alert)
- [ ] 정기 백업/복구 리허설 (PostgreSQL)
- [ ] 배포 후 자동 검증(헬스체크 + 주요 API smoke test)

---

## 5) 최소 전환 경로 (빠른 적용)

1. GitHub Secrets/Variables 등록  
2. `k8s/overlays/dev/kustomization.yaml`의 도메인/DB 호스트/ACR 경로 확정  
3. `deploy-dev.yml`로 dev AKS 배포 성공  
4. 트래픽/로그/오류 모니터링 안정화  
5. prod 값 반영 후 `deploy-prod.yml` 배포  

---

## 6) 완료 기준 (Definition of Done)

- [ ] dev/prod 모두 `kubectl rollout status` 성공
- [ ] `/api/v1/health` 외부 접근 정상
- [ ] 프론트에서 백엔드 API 호출 정상
- [ ] 보안 스캔(Trivy) 정책 통과
- [ ] 롤백 절차 1회 리허설 완료
- [ ] 문서(README + 가이드) 최신 상태 반영 완료

---

## 7) v1 점검 결과 요약 (현재 레포 기준)

- 완료([x]): **16개**
- 미완료/확인필요([ ]): **43개**
- 비고:
  - Azure/GitHub 실제 리소스/시크릿 값은 레포 내에서 검증 불가
  - `k8s/overlays/dev/kustomization.yaml`의 `ENVIRONMENT=development`는 `config.py`의 enum(`local/staging/production`)과 불일치 가능성이 있어 우선 수정 권장

---

## 8) Agent Platform 연동 반영 상태 (v1)

현재 레포에는 Agent 연동 v1 코드가 반영되어 있습니다.

- 백엔드
  - `api/v1/agents.py` 추가 (실행 생성/목록/단건 조회)
  - `models/agent_run.py`, `schemas/agent.py`, `crud/agent_run.py` 추가
  - `services/agent_client.py` 추가 (외부 Agent 플랫폼 호출)
  - `tasks/agent_tasks.py` 추가 (Celery 비동기 실행)
  - Alembic 마이그레이션 추가 (`add_agent_runs_table`)

- 프론트엔드
  - `app/dashboard/agents/page.tsx` 추가
  - `lib/api/agents.ts` 추가
  - 대시보드 메뉴에 Agent 실행 링크 추가

- AKS/운영 측 추가 점검 항목
  - [ ] `AGENT_PLATFORM_BASE_URL`, `AGENT_PLATFORM_RUN_PATH`를 `backend-config`에 반영
  - [ ] `AGENT_PLATFORM_API_KEY`를 `backend-secret`(또는 외부 시크릿 매니저)로 주입
  - [ ] Agent 플랫폼 네트워크 egress 허용 정책 점검
  - [ ] Agent 호출 실패/지연 모니터링 지표(로그/알람) 추가
