### **Plano de Execução: Saga 06 - Observabilidade com Logging Estruturado**

**Objetivo:** Implementar um sistema de logging que emita todas as saídas em formato JSON estruturado, preparando a aplicação para ser observável em ambientes de produção.

**Passos de Execução:**

**1. Criar a Estrutura do Módulo de Logging:**
   - Crie o diretório e o arquivo de configuração de logging.
     ```bash
     mkdir -p app/core
     touch app/core/logging_config.py
     touch app/core/__init__.py
     ```

**2. Implementar o Formatador JSON em `app/core/logging_config.py`:**
   - Adicione o código que cria um formatador de log customizado.
     ```python
     import json
     import logging
     import sys
     from datetime import datetime

     class JSONFormatter(logging.Formatter):
         def format(self, record: logging.LogRecord) -> str:
             log_entry = {
                 "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                 "level": record.levelname,
                 "name": record.name,
                 "message": record.getMessage(),
                 "module": record.module,
                 "function": record.funcName,
                 "line": record.lineno,
             }
             if record.exc_info:
                 log_entry["exception"] = self.formatException(record.exc_info)
             return json.dumps(log_entry, ensure_ascii=False)

     def configure_logging() -> None:
         # Remove handlers existentes para evitar duplicação
         root_logger = logging.getLogger()
         if root_logger.hasHandlers():
             root_logger.handlers.clear()

         handler = logging.StreamHandler(sys.stdout)
         handler.setFormatter(JSONFormatter())
         root_logger.addHandler(handler)
         root_logger.setLevel(logging.INFO)

         # Reduz a verbosidade de loggers de bibliotecas
         logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
         logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
     ```

**3. Integrar a Configuração na Aplicação Principal:**
   - No topo do arquivo `app/main.py`, importe e chame a nova função de configuração.
     ```python
     from fastapi import FastAPI
     from app import api, database, models
     from app.core.logging_config import configure_logging

     # Configura o logging como a primeira ação
     configure_logging()

     models.Base.metadata.create_all(bind=database.engine)
     # ... resto do arquivo
     ```

**4. Adicionar Loggers e Chamadas de Log:**
   - Adicione instâncias de logger e chamadas de log nos pontos chave da aplicação para que possamos ver o resultado.
   - **Em `app/api.py`:**
     ```python
     # Adicionar no topo
     import logging
     logger = logging.getLogger(__name__)

     # Adicionar dentro da função process_payout_batch
     logger.info(f"Payout batch received: {batch.batch_id}")
     ```
   - **Em `app/services.py`:**
     ```python
     # Adicionar no topo
     import logging
     logger = logging.getLogger(__name__)

     # Adicionar dentro da função process_batch
     logger.info(f"Processing {len(batch.items)} items for batch {batch.batch_id}")
     ```

---

**Critério de Sucesso:**
1.  A aplicação deve iniciar normalmente com `docker compose up`.
2.  Ao visualizar os logs com `docker compose logs api`, a saída deve estar em formato JSON.
3.  Ao fazer uma requisição para o endpoint `POST /api/v1/payouts/batch`, novas linhas de log devem aparecer no console, em formato JSON, contendo as mensagens que adicionamos.
