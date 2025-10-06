### **Plano de Execução: Saga 05 - API, Injeção de Dependência e Conclusão**

**Objetivo:** Integrar todas as camadas usando o sistema de injeção de dependência do FastAPI para fornecer uma sessão de banco de dados a cada requisição, e fazer o teste E2E da Saga 02 passar.

---

### **Passos de Execução**

**1. Implementar o Gerenciamento de Sessão de DB (`app/dependencies.py`):**
   - Crie ou atualize o arquivo `app/dependencies.py` para gerenciar o ciclo de vida da sessão do banco de dados e a validação da API Key.
     ```python
     from fastapi import Security, HTTPException, status
     from fastapi.security import APIKeyHeader
     from .database import SessionLocal
     from .core.config import settings

     # --- Segurança ---
     api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

     def validate_api_key(key: str = Security(api_key_header)):
         if not key or key != settings.API_KEY:
             raise HTTPException(
                 status_code=status.HTTP_401_UNAUTHORIZED,
                 detail="Invalid or missing API Key"
             )

     # --- Banco de Dados ---
     def get_db_session():
         db = None
         try:
             db = SessionLocal()
             yield db
         finally:
             if db:
                 db.close()
     ```

**2. Atualizar a Camada de API para Usar Dependências (`app/api.py`):**
   - Modifique `app/api.py` para injetar a sessão do banco de dados (`db: Session`) e a dependência de segurança.
     ```python
     from fastapi import APIRouter, Depends
     from sqlalchemy.orm import Session

     from .models import PayoutBatch, PayoutReport
     from .services import PayoutService
     from .dependencies import get_db_session, validate_api_key

     router = APIRouter()

     @router.post(
         "/payouts/batch",
         response_model=PayoutReport,
         tags=["Payouts"],
         dependencies=[Depends(validate_api_key)] # Protege o endpoint
     )
     def process_payout_batch(
         batch: PayoutBatch,
         db: Session = Depends(get_db_session)
     ) -> PayoutReport:
         service = PayoutService(db_session=db)
         return service.process_batch(batch)
     ```

**3. Atualizar o Teste E2E para Passar:**
   - O teste em `tests/test_payouts_api.py` é a peça final. Ele já deve ter sido atualizado na Saga 3.1 para incluir o header `X-API-Key`. Nenhuma mudança adicional é esperada aqui, mas a execução dele é o principal critério de sucesso.

---

**Critério de Sucesso:**
1.  Os arquivos `app/dependencies.py` e `app/api.py` devem estar atualizados.
2.  O comando `docker compose up --build -d` deve iniciar a aplicação e o banco de dados.
3.  O comando `docker compose exec api pytest` deve ser executado e o resultado esperado é **TODOS OS TESTES PASSANDO**, incluindo o teste E2E `test_process_batch_successfully`.
4.  Uma chamada `curl` com a `X-API-Key` correta e um payload de lote deve retornar um relatório de processamento bem-sucedido.