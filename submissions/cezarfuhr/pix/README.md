# Desafio Conty – PIX - @cezarfuhr

> **Local da submissão:** `submissions/cezarfuhr/pix`

Implementação do desafio de pagamentos em lote (PIX), com foco em idempotência, segurança e robustez para um ambiente de produção.

---

## Como Executar

Este projeto é 100% containerizado. Os únicos pré-requisitos são **Docker** e **Docker Compose**.

**1. Iniciar a Aplicação:**

Na raiz deste diretório (`pix/`), execute o script:

```sh
./run.sh
```

Isso irá construir as imagens e iniciar a API e o banco de dados. A API estará disponível em [http://localhost:8000](http://localhost:8000).

**2. Executar um Lote de Pagamentos (Exemplo):**

Use o comando `curl` abaixo para submeter um lote de pagamentos. A `API_KEY` está definida no arquivo `docker-compose.yml`.

```sh
curl -X POST "http://localhost:8000/api/v1/payouts/batch" \
-H "Content-Type: application/json" \
-H "X-API-Key: CONTY_CHALLENGE_SUPER_SECRET_KEY" \
-d \
'{
  "batch_id": "batch-`date +%s`",
  "items": [
    { "external_id": "user-a-001", "user_id": "u1", "amount_cents": 15000, "pix_key": "a@test.com" },
    { "external_id": "user-b-002", "user_id": "u2", "amount_cents": 25000, "pix_key": "b@test.com" }
  ]
}'
```

**3. Rodar os Testes:**

Para executar a suíte completa de testes (16 testes) com coverage, use o comando:

```sh
poetry run pytest
```

Ou apenas executar localmente:

```sh
PYTHONPATH=. poetry run pytest -v
```

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

---

## Uso de Inteligência Artificial (Primo IA Team)

Este projeto foi desenvolvido utilizando um fluxo de trabalho colaborativo entre humano e IAs, batizado de **Primo IA Team**.

- **Conductor (Humano - Cezar Fuhr):** Atuou como o líder do projeto, definindo a visão estratégica, tomando as decisões finais e guiando o trabalho das IAs.
- **Planner (IA - Gemini):** Atuou como o arquiteto e planejador, transformando os objetivos em planos de execução detalhados (sagas), revisando o código e garantindo a qualidade e a aderência à arquitetura.
- **Executor (IA - Claude):** Atuou como o implementador, executando os planos de forma precisa para gerar o código da aplicação e dos testes.
