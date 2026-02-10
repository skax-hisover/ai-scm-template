"""
헬스체크 API 테스트 (샘플).

[개발 표준]
- 테스트 함수명은 test_ 접두사를 사용합니다.
- 하나의 테스트 함수는 하나의 시나리오만 검증합니다.
"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """헬스체크 엔드포인트가 OK를 반환하는지 확인."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
