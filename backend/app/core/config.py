"""
애플리케이션 설정 모듈.

pydantic-settings를 사용하여 환경 변수를 타입-안전하게 관리합니다.
.env 파일 또는 시스템 환경 변수에서 값을 읽어옵니다.

[개발 표준]
- 새로운 설정 항목 추가 시 이 파일에 정의하고, .env.example에도 반영하세요.
- 환경별 분기가 필요한 경우 ENVIRONMENT 필드를 활용하세요.
- 시크릿 값은 반드시 환경 변수로 주입하세요 (코드에 하드코딩 금지).
"""

import secrets
import warnings
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    """CORS origin 문자열을 파싱합니다."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """애플리케이션 전역 설정."""

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    # --- 프로젝트 기본 ---
    PROJECT_NAME: str = "AI-SCM"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    API_V1_STR: str = "/api/v1"

    # --- 보안 ---
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1  # 1일
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [self.FRONTEND_HOST]

    # --- 프론트엔드 ---
    FRONTEND_HOST: str = "http://localhost:3000"

    # --- PostgreSQL ---
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "ai_scm_db"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """SQLAlchemy 데이터베이스 URL을 생성합니다."""
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg2",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    # --- Redis / Celery ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # --- 이메일 ---
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # --- 초기 관리자 ---
    FIRST_SUPERUSER: EmailStr = "admin@ai-scm.com"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"

    # --- 로깅 ---
    LOG_LEVEL: str = "INFO"

    # --- 모니터링 ---
    SENTRY_DSN: HttpUrl | None = None

    # --- Agent 플랫폼 연동 ---
    AGENT_PLATFORM_BASE_URL: str | None = None
    AGENT_PLATFORM_API_KEY: str | None = None
    AGENT_PLATFORM_RUN_PATH: str = "/v1/agents/runs"
    AGENT_REQUEST_TIMEOUT_SECONDS: int = 60
    AGENT_DEFAULT_MODEL: str = "default"

    # -----------------------------------------------------------------
    # 보안 검증: 기본 시크릿 값 사용 경고/차단
    # -----------------------------------------------------------------
    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", for security, please change it, at least for deployments.'
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD)
        return self


settings = Settings()  # type: ignore
