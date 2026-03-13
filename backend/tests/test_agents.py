"""
Agent 실행 API 테스트.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import get_password_hash
from app.main import app
from app.models.user import User


def _create_test_user(db: Session) -> User:
    user = User(
        email="agent-test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Agent Tester",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_agent_run_sync_success(client: TestClient, db: Session, monkeypatch) -> None:
    user = _create_test_user(db)

    def mock_invoke_agent_run(**_kwargs):
        return {
            "external_run_id": "external-123",
            "output_text": "테스트 응답",
            "raw_response": {"message": "ok"},
        }

    app.dependency_overrides[get_current_user] = lambda: user
    monkeypatch.setattr("app.api.v1.agents.invoke_agent_run", mock_invoke_agent_run)
    response = client.post("/api/v1/agents/runs", json={"agent_id": "default-agent", "input_text": "안녕?", "sync": True})
    app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "succeeded"
    assert body["output_text"] == "테스트 응답"


def test_list_agent_runs(client: TestClient, db: Session, monkeypatch) -> None:
    user = _create_test_user(db)

    def mock_invoke_agent_run(**_kwargs):
        return {
            "external_run_id": "external-456",
            "output_text": "목록 테스트",
            "raw_response": {"message": "ok"},
        }

    app.dependency_overrides[get_current_user] = lambda: user
    monkeypatch.setattr("app.api.v1.agents.invoke_agent_run", mock_invoke_agent_run)

    create_response = client.post(
        "/api/v1/agents/runs",
        json={
            "agent_id": "default-agent",
            "input_text": "목록 조회 테스트",
            "sync": True,
        },
    )
    assert create_response.status_code == 201

    response = client.get("/api/v1/agents/runs")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["data"][0]["agent_id"] == "default-agent"

