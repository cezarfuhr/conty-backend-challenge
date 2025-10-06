### **Plano de Execução: Saga 00 - A Fundação (do Zero)**

**Objetivo:** Criar um projeto "Hello World" em FastAPI, gerenciado por Poetry e containerizado com Docker/Docker Compose. Este plano serve como um registro de como a estrutura base foi concebida.

**Metadados do Projeto:**
*   **Nome do Pacote:** `conty_pix_challenge`
*   **Versão:** `0.1.0`
*   **Descrição:** `API para o desafio de pagamentos em lote da Conty.`
*   **Autor:** `Cezar Fuhr <cezar.fuhr@gmail.com>`
*   **Licença:** `MIT`
*   **Versão do Python:** `^3.11`

---

### **Passos de Implementação**

**1. Estrutura de Diretórios Inicial:**
   - [X] Criar os diretórios `app`, `tests`.

**2. Inicialização do Projeto Python com Poetry:**
   - [X] Executar `poetry init` com os metadados definidos.
   - [X] Executar `poetry config virtualenvs.in-project true`.
   - [X] Adicionar dependências de produção: `poetry add fastapi "uvicorn[standard]" pydantic-settings`.
   - [X] Adicionar dependências de desenvolvimento: `poetry add pytest httpx --group dev`.

**3. Esqueleto da Aplicação "Hello World":**
   - [X] Criar o arquivo `app/main.py` com um endpoint GET `/` que retorna `{"status": "ok"}`.

**4. Containerização com Docker:**
   - [X] Criar um arquivo `.gitignore` apropriado para projetos Python.
   - [X] Criar um arquivo `.dockerignore` para otimizar o contexto de build do Docker.
   - [X] Criar um `Dockerfile` multi-stage para construir uma imagem de produção otimizada, separando o build das dependências da imagem final.
   - [X] Criar um `docker-compose.yml` para orquestrar a execução do contêiner, mapeando a porta `8000` e montando o volume do código para `hot-reload`.

**5. Teste de Integração Inicial:**
   - [X] Criar `tests/test_api.py` para validar o endpoint `/`. O teste deve verificar se o status é `200` e o corpo da resposta é `{"status": "ok"}`.

**6. Documentação Inicial:**
   - [X] Criar um `README.md` inicial com o nome do projeto e uma breve descrição.

---
**Critério de Sucesso para esta Saga:**
Um comando `docker compose up --build` deve subir a aplicação. O acesso a `http://localhost:8000` deve retornar o JSON de status. O comando `docker compose exec api pytest` deve executar e passar os testes.
