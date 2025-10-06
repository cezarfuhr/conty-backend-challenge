### **Plano de Execução: Saga 03 - Repositório e Idempotência**

**Objetivo:** Implementar o `PayoutRepository` com persistência em memória. A funcionalidade principal será a lógica para garantir a idempotência, verificando a existência de um `external_id` antes de processar um novo pagamento.
