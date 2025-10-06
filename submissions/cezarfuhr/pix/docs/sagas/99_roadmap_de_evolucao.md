### **Plano de Evolução: Saga 99 - Roadmap para Produção**

**Objetivo:** Documentar um roadmap de melhorias técnicas que elevariam este serviço de um protótipo funcional para um sistema robusto, escalável e seguro, pronto para um ambiente de produção em larga escala.

---

### **Roadmap de Evolução**

#### **Tier 1: Fundamentos para Produção**

Estes são os próximos passos essenciais para que o serviço possa operar com segurança e estabilidade em um ambiente real.

1.  **Processamento Assíncrono de Lotes:**
    *   **Problema:** O processamento síncrono atual pode causar timeouts na API para lotes grandes e não é resiliente a falhas do servidor.
    *   **Solução:** Implementar uma arquitetura de Fila de Mensagens + Workers.
        *   **Fila:** Utilizar **RabbitMQ** ou **Redis** para enfileirar os lotes recebidos.
        *   **Workers:** Utilizar **Celery** para criar workers que consomem da fila e processam os pagamentos em background.
    *   **Impacto:** A resposta da API se torna instantânea (apenas confirma o recebimento), e o processamento se torna mais robusto e escalável (podemos adicionar mais workers conforme a demanda).

2.  **Gerenciamento Avançado de Credenciais:**
    *   **Problema:** Credenciais ainda estão em texto plano no `docker-compose.yml`.
    *   **Solução:** Integrar com um sistema de gerenciamento de segredos. A escolha depende do ambiente de deploy:
        *   **Docker:** Utilizar **Docker Secrets**.
        *   **Kubernetes:** Utilizar **Kubernetes Secrets**.
        *   **Cloud:** Utilizar o serviço nativo da nuvem (ex: **AWS Secrets Manager**, **GCP Secret Manager**, **Azure Key Vault**).

3.  **Gerenciamento de Migrações de Banco de Dados:**
    *   **Problema:** A criação de tabelas via `Base.metadata.create_all()` não permite versionamento ou alterações no esquema em produção sem risco de perda de dados.
    *   **Solução:** Integrar o **Alembic** para gerenciar o versionamento do esquema do banco de dados. Cada alteração na estrutura das tabelas se torna uma "migração" versionada e aplicável de forma segura.

#### **Tier 2: Observabilidade e Confiabilidade**

Com o básico de produção resolvido, o foco se volta para monitorar e garantir a confiabilidade contínua do serviço.

1.  **Métricas e Dashboards:**
    *   **Problema:** Logs são ótimos para investigar eventos, mas não para monitorar a saúde do sistema em tempo real.
    *   **Solução:**
        *   Exportar métricas de aplicação no padrão **Prometheus** (ex: latência, taxa de erros, pagamentos processados por segundo).
        *   Criar dashboards no **Grafana** para visualizar essas métricas e configurar alertas para desvios de comportamento.

2.  **Mecanismo de Retentativas (Retries):**
    *   **Problema:** Pagamentos podem falhar por razões transitórias (ex: instabilidade na rede ou no provedor PIX).
    *   **Solução:** Integrar aos workers Celery uma política de retentativas com *exponential backoff* para itens que falham, tentando reprocessá-los automaticamente algumas vezes antes de marcá-los como falha permanente.

#### **Tier 3: Maturidade e Ecossistema**

Passos para solidificar o serviço como um componente maduro dentro de um ecossistema de TI maior.

1.  **Pipeline Completo de CI/CD:**
    *   **Problema:** O processo de build e deploy ainda é manual.
    *   **Solução:** Criar um pipeline no **GitHub Actions** (ou similar) que automatiza todo o ciclo: `push -> lint -> test -> build -> publish (Docker image) -> deploy`.

2.  **Rastreamento Distribuído (Distributed Tracing):**
    *   **Problema:** Se este serviço chamar outros (ou for chamado por outros), fica difícil rastrear o fluxo de uma requisição.
    *   **Solução:** Integrar o **OpenTelemetry** para adicionar IDs de correlação a todas as operações (chamadas de API, jobs na fila, queries no banco), permitindo uma visão completa do ciclo de vida de uma transação em ferramentas como **Jaeger** ou **Datadog APM**.