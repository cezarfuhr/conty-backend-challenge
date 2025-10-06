import os
os.environ['API_KEY'] = 'test-key'

import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_process_batch_no_api_key():
    """Teste sem chave de API - deve retornar 401"""
    response = client.post("/api/v1/payouts/batch", json={})
    assert response.status_code == 401

def test_process_batch_wrong_api_key():
    """Teste com chave de API incorreta - deve retornar 401"""
    headers = {"X-API-Key": "wrong-key"}
    response = client.post("/api/v1/payouts/batch", json={}, headers=headers)
    assert response.status_code == 401

def test_process_batch_successfully():
    """
    Testa o processamento de um lote com sucesso.
    Mock do simulate_payment para garantir 100% de sucesso.
    """
    headers = {"X-API-Key": settings.API_KEY}

    # Gera IDs unicos para evitar duplicatas entre execucoes
    unique_id_1 = f"e2e-{uuid.uuid4().hex[:8]}"
    unique_id_2 = f"e2e-{uuid.uuid4().hex[:8]}"

    payload = {
        "batch_id": "2025-10-06-A",
        "items": [
            { "external_id": unique_id_1, "user_id": "u1", "amount_cents": 35000, "pix_key": "u1@email.com" },
            { "external_id": unique_id_2, "user_id": "u2", "amount_cents": 120000, "pix_key": "+55 11 91234-5678" }
        ]
    }

    # Mock para garantir 100% de sucesso
    with patch('app.services.PayoutService._simulate_payment', return_value=True):
        response = client.post("/api/v1/payouts/batch", json=payload, headers=headers)

    assert response.status_code == 200

    report = response.json()
    assert report["batch_id"] == "2025-10-06-A"
    assert report["processed"] == 2
    assert report["successful"] == 2
    assert report["failed"] == 0
    assert report["duplicates"] == 0
    assert len(report["details"]) == 2
    assert report["details"][0]["status"] == "paid"
    assert report["details"][1]["status"] == "paid"
