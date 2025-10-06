### **Plano de Execução: Saga 05 - API, Injeção de Dependência e Conclusão**

**Objetivo:** Integrar todas as camadas usando o sistema de injeção de dependência do FastAPI para fornecer uma sessão de banco de dados a cada requisição, e fazer o teste E2E da Saga 02 passar.

---

### **Passos de Execução**

**1. Implementar o Gerenciamento de Sessão de DB (`app/dependencies.py`):**
   - Crie um novo arquivo `app/dependencies.py` para gerenciar o ciclo de vida da sessão do banco de dados.
     ```python
     from .database import SessionLocal

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
   - Modifique `app/api.py` para injetar a sessão do banco de dados (`db: Session`) e então criar o serviço com essa sessão.
     ```python
     from fastapi import APIRouter, Depends
     from sqlalchemy.orm import Session

     from .models import PayoutBatch, PayoutReport
     from .services import PayoutService
     from .dependencies import get_db_session

     router = APIRouter()

     @router.post("/payouts/batch", response_model=PayoutReport, tags=["Payouts"])
     def process_payout_batch(
         batch: PayoutBatch,
         db: Session = Depends(get_db_session)
     ) -> PayoutReport:
         service = PayoutService(db_session=db)
         return service.process_batch(batch)
     ```

**3. Remover Instanciação Manual do Serviço:**
   - O `app/services.py` já está correto da saga anterior, recebendo a sessão do DB no construtor. Nenhuma mudança é necessária aqui.

**4. Garantir que o Teste E2E Use o Banco de Testes:**
   - O teste E2E usará o mesmo `docker-compose.yml`, então ele rodará contra a instância de banco de dados de teste, o que é o comportamento desejado. Nenhuma mudança é necessária no arquivo `tests/test_payouts_api.py`.

---

**Critério de Sucesso:**
1.  Os arquivos `app/dependencies.py` e `app/api.py` devem ser criados/atualizados.
2.  O comando `docker compose up --build -d` deve iniciar a aplicação e o banco de dados.
3.  O comando `docker compose exec api pytest` deve ser executado e o resultado esperado é **TODOS OS TESTES PASSANDO**, incluindo o teste E2E `test_process_batch_successfully`.
4.  Uma chamada `curl` com um payload de lote deve retornar um relatório de processamento bem-sucedido.
