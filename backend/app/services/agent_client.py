"""
외부 Agent 플랫폼 연동 클라이언트.
"""

from typing import Any

import httpx

from app.core.config import settings


def invoke_agent_run(
    *,
    agent_id: str,
    input_text: str,
    model_name: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    외부 Agent 플랫폼 API를 호출합니다.

    반환 형식(권장):
        {
            "external_run_id": "...",
            "output_text": "...",
            "raw_response": {...}
        }
    """
    base_url = settings.AGENT_PLATFORM_BASE_URL
    if not base_url:
        raise ValueError("AGENT_PLATFORM_BASE_URL이 설정되지 않았습니다")

    run_path = settings.AGENT_PLATFORM_RUN_PATH
    url = f"{base_url.rstrip('/')}/{run_path.lstrip('/')}"

    payload: dict[str, Any] = {
        "agent_id": agent_id,
        "input": input_text,
        "model": model_name or settings.AGENT_DEFAULT_MODEL,
        "metadata": metadata or {},
    }

    headers = {"Content-Type": "application/json"}
    if settings.AGENT_PLATFORM_API_KEY:
        headers["Authorization"] = f"Bearer {settings.AGENT_PLATFORM_API_KEY}"

    timeout = settings.AGENT_REQUEST_TIMEOUT_SECONDS
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        body = response.json()

    output_text = body.get("output") or body.get("result") or body.get("message") or body.get("text") or ""
    external_run_id = body.get("run_id") or body.get("id")
    return {
        "external_run_id": external_run_id,
        "output_text": str(output_text),
        "raw_response": body,
    }
