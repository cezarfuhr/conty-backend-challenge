from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_process_batch_successfully():
    """
    Testa o processamento de um lote com sucesso.
    Este teste DEVE FALHAR ate a Saga 05.
    """
    payload = {
        "batch_id": "2025-10-06-A",
        "items": [
            { "external_id": "u1-001", "user_id": "u1", "amount_cents": 35000, "pix_key": "u1@email.com" },
            { "external_id": "u2-002", "user_id": "u2", "amount_cents": 120000, "pix_key": "+55 11 91234-5678" }
        ]
    }

    response = client.post("/api/v1/payouts/batch", json=payload)

    assert response.status_code == 200

    report = response.json()
    assert report["batch_id"] == "2025-10-06-A"
    assert report["processed"] == 2
    assert report["successful"] == 2
    assert report["failed"] == 0
    assert report["duplicates"] == 0
    assert len(report["details"]) == 2
    assert report["details"][0]["status"] == "paid"
