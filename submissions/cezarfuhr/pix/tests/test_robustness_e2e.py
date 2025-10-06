import os
os.environ['API_KEY'] = 'test-key'

import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services import PayoutService

client = TestClient(app)


def test_double_submission_is_idempotent():
    """Garante que submeter o mesmo lote duas vezes resulta em duplicatas."""
    headers = {"X-API-Key": settings.API_KEY}

    # Gera IDs unicos para evitar conflitos entre execucoes
    unique_id_1 = f"idem-{uuid.uuid4().hex[:8]}"
    unique_id_2 = f"idem-{uuid.uuid4().hex[:8]}"

    payload = {
        "batch_id": "idempotency-test-01",
        "items": [
            { "external_id": unique_id_1, "user_id": "u1", "amount_cents": 100, "pix_key": "a@a.com" },
            { "external_id": unique_id_2, "user_id": "u2", "amount_cents": 200, "pix_key": "b@b.com" }
        ]
    }

    # 1. Primeira submissao: deve processar 2 com sucesso
    with patch.object(PayoutService, '_simulate_payment', return_value=True):
        response1 = client.post("/api/v1/payouts/batch", json=payload, headers=headers)
        assert response1.status_code == 200
        report1 = response1.json()
        assert report1["successful"] == 2
        assert report1["duplicates"] == 0

    # 2. Segunda submissao: deve detectar 2 duplicatas
    with patch.object(PayoutService, '_simulate_payment', return_value=True):
        response2 = client.post("/api/v1/payouts/batch", json=payload, headers=headers)
        assert response2.status_code == 200
        report2 = response2.json()
        assert report2["successful"] == 0
        assert report2["duplicates"] == 2


def test_failed_item_can_be_resubmitted():
    """Garante que um item que falhou pode ser reprocessado com sucesso."""
    headers = {"X-API-Key": settings.API_KEY}

    # Gera ID unico para evitar conflitos entre execucoes
    unique_id = f"fail-{uuid.uuid4().hex[:8]}"

    payload = {
        "batch_id": "failure-test-01",
        "items": [{ "external_id": unique_id, "user_id": "u3", "amount_cents": 300, "pix_key": "c@c.com" }]
    }

    # 1. Simula uma falha no pagamento
    with patch.object(PayoutService, '_simulate_payment', return_value=False):
        response1 = client.post("/api/v1/payouts/batch", json=payload, headers=headers)
        assert response1.status_code == 200
        assert response1.json()["failed"] == 1

    # 2. Simula um sucesso no pagamento para o mesmo item
    with patch.object(PayoutService, '_simulate_payment', return_value=True):
        response2 = client.post("/api/v1/payouts/batch", json=payload, headers=headers)
        assert response2.status_code == 200
        report2 = response2.json()
        assert report2["successful"] == 1
        assert report2["failed"] == 0
        assert report2["duplicates"] == 0  # Nao e duplicata, pois a falha nao foi persistida
