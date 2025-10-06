### **Plano de Execução: Saga 07 - Testes Avançados de Robustez**

**Objetivo:** Fortalecer a confiança no sistema através da criação de testes End-to-End específicos para os cenários mais críticos de idempotência e segurança de dados.

---

### **Passos de Execução**

**1. Criar Novo Arquivo de Teste:**
   - Para manter a organização, crie um novo arquivo de teste dedicado a estes cenários de robustez.
     ```bash
     touch tests/test_robustness_e2e.py
     ```

**2. Implementar Teste de Submissão Dupla (Idempotência):**
   - Em `tests/test_robustness_e2e.py`, adicione o seguinte teste:
     ```python
     from fastapi.testclient import TestClient
     from app.main import app
     from app.core.config import settings

     client = TestClient(app)

     def test_double_submission_is_idempotent():
         """Garante que submeter o mesmo lote duas vezes resulta em duplicatas."""
         headers = {"X-API-Key": settings.API_KEY}
         payload = {
             "batch_id": "idempotency-test-01",
             "items": [
                 { "external_id": "idem-001", "user_id": "u1", "amount_cents": 100, "pix_key": "a@a.com" },
                 { "external_id": "idem-002", "user_id": "u2", "amount_cents": 200, "pix_key": "b@b.com" }
             ]
         }

         # 1. Primeira submissão: deve processar 2 com sucesso
         response1 = client.post("/api/v1/payouts/batch", json=payload, headers=headers)
         assert response1.status_code == 200
         report1 = response1.json()
         assert report1["successful"] == 2
         assert report1["duplicates"] == 0

         # 2. Segunda submissão: deve detectar 2 duplicatas
         response2 = client.post("/api/v1/payouts/batch", json=payload, headers=headers)
         assert response2.status_code == 200
         report2 = response2.json()
         assert report2["successful"] == 0
         assert report2["duplicates"] == 2
     ```

**3. Implementar Teste de Reenvio Após Falha (Idempotência):**
   - Este teste é mais complexo, pois precisamos controlar o comportamento da simulação de pagamento. Usaremos o `dependency_overrides` do FastAPI para injetar um serviço "mockado".
   - Adicione este teste ao `tests/test_robustness_e2e.py`:
     ```python
     from unittest.mock import patch
     from app.services import PayoutService

     def test_failed_item_can_be_resubmitted():
         """Garante que um item que falhou pode ser reprocessado com sucesso."""
         headers = {"X-API-Key": settings.API_KEY}
         payload = {
             "batch_id": "failure-test-01",
             "items": [{ "external_id": "fail-then-succeed", "user_id": "u3", "amount_cents": 300, "pix_key": "c@c.com" }]
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
             assert report2["duplicates"] == 0 # Não é duplicata, pois a falha não foi persistida
     ```

---

**Critério de Sucesso:**
1.  O novo arquivo `tests/test_robustness_e2e.py` deve ser criado.
2.  Todos os testes da suíte, incluindo os novos testes de robustez, devem passar com sucesso após a conclusão das Sagas 0-5.
