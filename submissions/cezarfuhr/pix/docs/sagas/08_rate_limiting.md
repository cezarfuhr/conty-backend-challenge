### **Plano de Execução: Saga 08 - Implementação de Rate Limiting**

**Objetivo:** Proteger a API contra abuso e sobrecarga implementando um limite de requisições (rate limiting) no endpoint de processamento de lotes.

---

### **Passos de Execução**

**1. Adicionar a Dependência `slowapi`:**
   - Adicione a biblioteca que facilitará a implementação do rate limiting.
     ```bash
     poetry add slowapi
     ```

**2. Criar e Configurar o Limitador:**
   - Crie um novo arquivo `app/limiter.py` para centralizar a configuração do rate limiter.
     ```python
     from slowapi import Limiter
     from slowapi.util import get_remote_address

     # O limiter usará o endereço de IP do cliente como chave
     limiter = Limiter(key_func=get_remote_address)
     ```

**3. Integrar o `slowapi` com o FastAPI:**
   - Em `app/main.py`, importe o limiter, adicione-o ao estado da aplicação e registre o handler de exceção para quando o limite for excedido.
     ```python
     # Adicionar no topo de app/main.py
     from app.limiter import limiter
     from slowapi.errors import RateLimitExceeded
     from slowapi.middleware import SlowAPIMiddleware
     from starlette.requests import Request
     from starlette.responses import JSONResponse

     # ... (após a chamada de configure_logging)
     app = FastAPI(title="Conty PIX Challenge")
     app.state.limiter = limiter
     app.add_middleware(SlowAPIMiddleware)

     @app.exception_handler(RateLimitExceeded)
     async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
         return JSONResponse(
             status_code=429,
             content={"detail": f"Rate limit exceeded: {exc.detail}"}
         )
     
     # ... (resto do arquivo)
     ```

**4. Proteger o Endpoint Específico:**
   - Em `app/api.py`, importe o limiter e aplique o decorador ao endpoint de processamento de lotes.
     ```python
     # Adicionar no topo de app/api.py
     from app.limiter import limiter

     # Adicionar o decorador na função process_payout_batch
     @router.post(...)
     @limiter.limit("5/minute") # Limite de 5 requisições por minuto por IP
     def process_payout_batch(...):
         # ... (código da função)
     ```

**5. Criar Teste para o Rate Limiter:**
   - Crie um novo arquivo `tests/test_rate_limiter.py` para testar especificamente esta funcionalidade.
     ```python
     from fastapi.testclient import TestClient
     from app.main import app
     from app.core.config import settings

     # É preciso instanciar o cliente com um IP base para o teste
     client = TestClient(app, base_url="http://testserver.local")

     def test_rate_limit_is_enforced():
         """Garante que o endpoint retorna 429 após exceder o limite."""
         headers = {"X-API-Key": settings.API_KEY}
         payload = {"batch_id": "rate-limit-test", "items": []}

         # 5 requisições devem passar
         for i in range(5):
             response = client.post("/api/v1/payouts/batch", json=payload, headers=headers)
             assert response.status_code != 429, f"Request {i+1} failed unexpectedly"

         # A 6ª requisição deve falhar
         response = client.post("/api/v1/payouts/batch", json=payload, headers=headers)
         assert response.status_code == 429
         assert "Rate limit exceeded" in response.json()["detail"]
     ```

---

**Critério de Sucesso:**
1.  A aplicação deve rodar com a nova dependência.
2.  O novo teste em `tests/test_rate_limiter.py` deve passar.
3.  Ao testar manualmente (ex: com `curl`), a 6ª requisição para o endpoint dentro de um minuto deve retornar um erro `HTTP 429 Too Many Requests`.
