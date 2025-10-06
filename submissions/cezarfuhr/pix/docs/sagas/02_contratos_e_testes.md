### **Plano de Execução: Saga 02 - Contratos e Esqueleto de Testes**

**Objetivo:** Definir todos os modelos de dados (contratos) da aplicação, criar a estrutura inicial dos serviços e repositórios, e escrever o teste End-to-End (E2E) que validará o ciclo de vida completo do processamento de um lote. **Este teste E2E deve falhar ao final da saga.**

---

### **Passos de Execução**

**1. Criar Arquivos para as Novas Camadas:**
   - Crie os seguintes arquivos vazios. Eles abrigarão nossos modelos, serviços, repositórios e a nova rota da API.
     ```bash
     touch app/models.py app/repository.py app/services.py app/api.py tests/test_payouts_api.py
     ```

**2. Definir os Modelos de Dados (Contratos) em `app/models.py`:**
   - Substitua o conteúdo de `app/models.py` pelo código abaixo. Estes são os modelos Pydantic que definem a estrutura de entrada e saída da nossa API.
     ```python
     from pydantic import BaseModel, Field
     from typing import List

     class PayoutItem(BaseModel):
         external_id: str
         user_id: str
         amount_cents: int
         pix_key: str

     class PayoutBatch(BaseModel):
         batch_id: str
         items: List[PayoutItem]

     class PayoutDetail(BaseModel):
         external_id: str
         status: str
         amount_cents: int

     class PayoutReport(BaseModel):
         batch_id: str
         processed: int
         successful: int
         failed: int
         duplicates: int
         details: List[PayoutDetail]
     ```

**3. Criar Esqueletos do Repositório e Serviço:**
   - Em `app/repository.py`, adicione a classe `PayoutRepository`.
     ```python
     class PayoutRepository:
         def find_by_external_id(self, external_id: str):
             # A ser implementado na Saga 03
             pass

         def save_payout(self, payout_detail):
             # A ser implementado na Saga 03
             pass
     ```
   - Em `app/services.py`, adicione a classe `PayoutService`.
     ```python
     from .models import PayoutBatch, PayoutReport
     from .repository import PayoutRepository

     class PayoutService:
         def __init__(self):
             # Em uma aplicação real, injetaríamos a dependência.
             self.repository = PayoutRepository()

         def process_batch(self, batch: PayoutBatch) -> PayoutReport:
             # Lógica a ser implementada na Saga 04.
             # Retorno hardcoded para o teste E2E falhar de forma previsível.
             return PayoutReport(
                 batch_id=batch.batch_id,
                 processed=0,
                 successful=0,
                 failed=len(batch.items),
                 duplicates=0,
                 details=[]
             )
     ```

**4. Criar o Esqueleto da API em `app/api.py`:**
   - Adicione o código do novo router que expõe o endpoint de pagamentos.
     ```python
     from fastapi import APIRouter
     from .models import PayoutBatch, PayoutReport
     from .services import PayoutService

     router = APIRouter()

     @router.post("/payouts/batch", response_model=PayoutReport, tags=["Payouts"])
     def process_payout_batch(batch: PayoutBatch) -> PayoutReport:
         service = PayoutService()
         return service.process_batch(batch)
     ```

**5. Integrar o Novo Router no `app/main.py`:**
   - Modifique o `app/main.py` para importar e incluir o novo router da API.
     ```python
     from fastapi import FastAPI
     from app import api # Importe o módulo da api

     app = FastAPI(title="Conty PIX Challenge")

     app.include_router(api.router, prefix="/api/v1") # Inclua o router

     @app.get("/", tags=["Health Check"])
     def read_root():
         return {"status": "ok"}
     ```

**6. Escrever o Teste E2E (que deve falhar):**
   - Em `tests/test_payouts_api.py`, adicione o teste de ciclo de vida.
     ```python
     from fastapi.testclient import TestClient
     from app.main import app

     client = TestClient(app)

     def test_process_batch_successfully():
         """
         Testa o processamento de um lote com sucesso.
         Este teste DEVE FALHAR até a Saga 05.
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
     ```

---

**Critério de Sucesso:**
1.  Todos os novos arquivos devem ser criados.
2.  A aplicação deve iniciar sem erros com `docker compose up`.
3.  O comando `docker compose exec api pytest` deve ser executado.
4.  O resultado dos testes deve ser: **1 PASSED** (`test_read_root`) e **1 FAILED** (`test_process_batch_successfully`).