"""
문자열 유틸리티.
"""

import secrets


def mask_email(email: str) -> str:
    """
    이메일 마스킹.

    예: "user@example.com" → "us***@example.com"
    """
    if "@" not in email:
        return email
    local, domain = email.split("@", 1)
    masked_local = local[0] + "***" if len(local) <= 2 else local[:2] + "***"
    return f"{masked_local}@{domain}"


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    문자열을 최대 길이로 자릅니다.

    예: truncate("Hello World", 8) → "Hello..."
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def generate_random_string(length: int = 32) -> str:
    """URL-safe 랜덤 문자열을 생성합니다."""
    return secrets.token_urlsafe(length)


def to_snake_case(name: str) -> str:
    """CamelCase를 snake_case로 변환합니다."""
    result: list[str] = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append("_")
        result.append(char.lower())
    return "".join(result)
