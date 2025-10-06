import os
os.environ['API_KEY'] = 'test-key'

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

# E preciso instanciar o cliente com um IP base para o teste
client = TestClient(app, base_url="http://testserver.local")


def test_rate_limit_is_enforced():
    """Garante que o endpoint retorna 429 apos exceder o limite."""
    headers = {"X-API-Key": settings.API_KEY}
    payload = {"batch_id": "rate-limit-test", "items": []}

    # 5 requisicoes devem passar
    for i in range(5):
        response = client.post("/api/v1/payouts/batch", json=payload, headers=headers)
        assert response.status_code != 429, f"Request {i+1} failed unexpectedly"

    # A 6a requisicao deve falhar
    response = client.post("/api/v1/payouts/batch", json=payload, headers=headers)
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]
