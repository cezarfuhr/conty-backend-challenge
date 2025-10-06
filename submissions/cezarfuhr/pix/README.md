# Desafio Conty – PIX - @cezarfuhr

> **Local da submissão:** `submissions/cezarfuhr/pix`

Implementação do desafio de pagamentos em lote (PIX), com foco em idempotência, segurança e robustez para um ambiente de produção.

---

## 🚀 Quick Start

### Pré-requisitos
- **Docker** e **Docker Compose** (para rodar a aplicação)
- **Poetry** (para rodar os testes localmente)

### 1. Setup Inicial

Clone o repositório e entre no diretório:

```bash
cd submissions/cezarfuhr/pix
```

Configure as variáveis de ambiente (opcional, já tem defaults):

```bash
cp .env.example .env
```

### 2. Iniciar a Aplicação (Docker)

Execute o script de inicialização:

```bash
./run.sh
```

Isso irá:
- Construir as imagens Docker
- Iniciar PostgreSQL e a API
- A API estará disponível em http://localhost:8000

**Verificar Health:**

```bash
curl http://localhost:8000/health
# Retorna: {"status":"healthy","timestamp":...,"checks":{"database":"healthy",...}}
```

### 3. Testar a API

Submeta um lote de pagamentos:

```bash
curl -X POST "http://localhost:8000/api/v1/payouts/batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: CONTY_CHALLENGE_SUPER_SECRET_KEY" \
  -d '{
    "batch_id": "batch-test-001",
    "items": [
      { "external_id": "user-a-001", "user_id": "u1", "amount_cents": 15000, "pix_key": "a@test.com" },
      { "external_id": "user-b-002", "user_id": "u2", "amount_cents": 25000, "pix_key": "b@test.com" }
    ]
  }'
```

**Testar Idempotência** (reenvie o mesmo lote):

```bash
# Mesmo comando acima - verá duplicates: 2
```

**Testar Rate Limiting** (envie 6+ requests rápidas):

```bash
# 6ª request retornará: HTTP 429 Too Many Requests
```

### 4. Rodar os Testes

**Com coverage (recomendado):**

```bash
poetry install
poetry run pytest
```

**Verbose mode:**

```bash
PYTHONPATH=. poetry run pytest -v
```

**Resultados esperados:**
- ✅ 16 testes passando
- 📊 90% code coverage
- 📄 Relatório HTML em `htmlcov/index.html`

---

## 📡 Endpoints da API

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/` | Health check simples | ❌ |
| `GET` | `/health` | Health check completo (DB, version) | ❌ |
| `POST` | `/api/v1/payouts/batch` | Processar lote de pagamentos | ✅ |

**Autenticação:**
- Header: `X-API-Key: CONTY_CHALLENGE_SUPER_SECRET_KEY`

**Rate Limiting:**
- 5 requisições por minuto por IP
- Retorna `HTTP 429` quando excedido

---

## Arquitetura e Decisões de Design

Esta solução foi projetada como um microsserviço robusto, seguindo os princípios de uma arquitetura limpa (Ports and Adapters) para garantir separação de responsabilidades e testabilidade.

```mermaid
graph TD
    A[Cliente API] --> B[API Layer (FastAPI)];
    B --> C[Service Layer];
    C --> D[Repository Layer];
    D --> E[DB (PostgreSQL)];

    subgraph "API Layer"
        B1["/api/v1/payouts/batch"]
        B2[Segurança: API Key & Rate Limiting]
        B3[Validação de Payload (Pydantic)]
    end

    subgraph "Service Layer"
        C1[PayoutService]
        C2[Lógica de Negócio]
        C3[Simulação de Pagamento]
    end

    subgraph "Repository Layer"
        D1[PayoutRepository]
        D2[Abstração do Banco]
        D3[Garantia de Idempotência]
    end

    B -- Injeção de Dependência --> C;
    C -- Interage com --> D;
```

### Principais Features

- **Idempotência:** Garantida na camada de banco de dados através de `UNIQUE CONSTRAINT` na coluna `external_id` - a abordagem mais segura contra *race conditions*
- **Segurança:**
  - Autenticação via `X-API-Key` header
  - Rate limiting (5 req/min por IP) com `slowapi`
  - Dados sensíveis (`pix_key`) mascarados com `SecretStr`
- **Validações Robustas:**
  - Valores positivos para `amount_cents` (> 0)
  - Limite máximo de 100M centavos por transação
  - IDs não podem ser vazios (min_length=1)
  - Batch deve ter pelo menos 1 item
  - Whitespace trimming automático
- **Observabilidade:**
  - Logs JSON estruturados com métricas (batch_id, counts, processing_time)
  - Health check rico em `/health` (database connectivity, version, status)
  - Coverage report configurado (pytest-cov)
- **Qualidade:**
  - 16 testes (E2E, unitários, validação, robustez, rate limiting)
  - 0 warnings de deprecation
  - Type hints completos

### Trade-offs e Decisões

**Decisões tomadas:**
- ✅ Idempotência via DB constraint (não em-memory) - mais seguro, survives restarts
- ✅ Simulação aleatória 95% sucesso - realista para testes de retry
- ✅ Rate limiting por IP - simples e efetivo para API pública
- ✅ Logs estruturados JSON - pronto para agregadores (ELK, Datadog)
- ✅ Repository pattern - desacopla lógica de persistência

**Com mais tempo, faria:**
- 🔄 Retry automático com exponential backoff para falhas transitórias
- 🔄 Dead Letter Queue (DLQ) para itens que falharam múltiplas vezes
- 🔄 Webhook callback para notificar cliente do resultado do batch
- 🔄 Métricas Prometheus (`/metrics`) para alertas e dashboards
- 🔄 Circuit breaker no provedor de pagamento externo
- 🔄 Compressão de payloads grandes (gzip)
- 🔄 Rate limiting mais sofisticado (por API key, tiered plans)
- 🔄 Async processing com Celery/RQ para batches grandes (>1000 items)

---

## 🤖 Uso de IA e Bibliotecas de Terceiros

### Uso de Inteligência Artificial (Primo IA Team)

Este projeto foi desenvolvido utilizando um fluxo de trabalho colaborativo entre humano e IAs:

- **Conductor (Humano - Cezar Fuhr):** Líder do projeto, definiu visão estratégica, decisões finais e guiou o trabalho das IAs
- **Planner (IA - Gemini):** Arquiteto e planejador, criou planos de execução detalhados (sagas), revisou código e garantiu qualidade
- **Executor (IA - Claude Code):** Implementador, executou os planos gerando código da aplicação e testes

**O que foi gerado por IA:**
- ~95% do código (seguindo arquitetura definida pelo Planner)
- 100% dos testes automatizados
- Estrutura do projeto e configurações
- Documentação inicial

**O que é autoria humana:**
- Visão e estratégia do projeto
- Decisões arquiteturais (Clean Architecture, Repository Pattern)
- Escolha de tecnologias (FastAPI, PostgreSQL, slowapi)
- Revisão e aprovação de todos os planos (sagas)
- Definição de critérios de qualidade (90% coverage, 0 warnings)

### Bibliotecas de Terceiros

| Biblioteca | Versão | Uso | Licença |
|------------|--------|-----|---------|
| `fastapi` | ^0.116.1 | Framework web | MIT |
| `uvicorn` | ^0.35.0 | ASGI server | BSD |
| `pydantic` | ^2.x | Validação de dados | MIT |
| `pydantic-settings` | ^2.10.1 | Config management | MIT |
| `sqlalchemy` | ^2.0.43 | ORM | MIT |
| `psycopg2-binary` | ^2.9.10 | PostgreSQL driver | LGPL |
| `slowapi` | ^0.1.9 | Rate limiting | MIT |
| `pytest` | ^8.4.1 | Testing framework | MIT |
| `pytest-cov` | ^7.0.0 | Coverage reporting | MIT |
| `httpx` | ^0.28.1 | HTTP client (testes) | BSD |

**Código 100% próprio (sem cópia):**
- Toda a lógica de negócio (`app/services.py`)
- Camada de repositório com idempotência (`app/repository.py`)
- Modelos de dados (`app/models.py`)
- Configurações e estrutura (`app/dependencies.py`, `app/api.py`)
- Toda a suíte de testes (16 testes únicos)
