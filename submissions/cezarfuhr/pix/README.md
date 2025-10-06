# Desafio Conty – PIX - @cezarfuhr

> **Local da submissão:** `submissions/cezarfuhr/pix`

Implementação do desafio de pagamentos em lote, focado em idempotência e confiabilidade.

## Como rodar

- **Requisitos:** Docker e Docker Compose.
- **Comando:** `./run.sh`
- **Variáveis de Ambiente:** Nenhuma no momento. Ver `app/core/config.py` para futuras configurações.

Após a execução, a API estará disponível em [http://localhost:8000](http://localhost:8000) e a documentação interativa em [http://localhost:8000/docs](http://localhost:8000/docs).

## Endpoints/CLI

*A ser definido na Saga 03.*

## Arquitetura

*A ser detalhada nas próximas sagas. A base segue uma arquitetura limpa (Ports and Adapters) com camadas de API, Serviço e Repositório.*

## Testes

Para rodar a suíte de testes, execute o comando abaixo no terminal, na raiz deste projeto (`pix/`):

```sh
docker compose exec api pytest
```

## IA/Libraries

- **IA:** O planejamento e a revisão de código são feitos por uma instância de Gemini (agindo como Arquiteto), e a implementação é delegada a uma instância de Claude (agindo como Implementador).
- **Bibliotecas Principais:** FastAPI, Uvicorn, Pydantic, Pytest.