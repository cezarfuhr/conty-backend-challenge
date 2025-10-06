### **Plano de Execução: Saga 03 - Integração com Postgres e Repositório**

**Objetivo:** Integrar a aplicação com um banco de dados Postgres via Docker Compose e implementar o `PayoutRepository` para persistir os dados, garantindo a idempotência a nível de banco de dados.

---

### **Passos de Execução**

**1. Adicionar Dependências de Banco de Dados:**
   - Adicione as bibliotecas necessárias para interagir com o Postgres ao `pyproject.toml`.
     ```bash
     poetry add sqlalchemy "psycopg2-binary"
     ```

**2. Atualizar o `docker-compose.yml`:**
   - Adicione um serviço de banco de dados `postgres` e configure a aplicação para esperar por ele.
     ```yaml
     version: '3.8'

     services:
       api:
         build: .
         ports:
           - "8000:8000"
         volumes:
           - ./app:/app/app
         depends_on:
           - db
         environment:
           - DATABASE_URL=postgresql://user:password@db:5432/payouts_db

       db:
         image: postgres:15-alpine
         volumes:
           - postgres_data:/var/lib/postgresql/data/
         environment:
           - POSTGRES_USER=user
           - POSTGRES_PASSWORD=password
           - POSTGRES_DB=payouts_db

     volumes:
       postgres_data:
     ```

**3. Criar Módulo de Banco de Dados (`app/database.py`):**
   - Crie um arquivo para gerenciar a conexão e a sessão com o banco de dados.
     ```python
     from sqlalchemy import create_engine
     from sqlalchemy.ext.declarative import declarative_base
     from sqlalchemy.orm import sessionmaker
     import os

     DATABASE_URL = os.environ.get("DATABASE_URL")

     engine = create_engine(DATABASE_URL)
     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
     Base = declarative_base()
     ```

**4. Definir o Modelo da Tabela (`app/models.py`):**
   - Adicione o modelo SQLAlchemy que representará nossa tabela no banco de dados, incluindo a constraint de unicidade para idempotência.
     ```python
     # Adicionar ao final de app/models.py
     from sqlalchemy import Column, String, Integer, UniqueConstraint
     from .database import Base

     class PayoutDB(Base):
         __tablename__ = "payouts"

         id = Column(Integer, primary_key=True, index=True)
         external_id = Column(String, unique=True, index=True)
         status = Column(String)
         amount_cents = Column(Integer)
     ```

**5. Modificar o `app/main.py` para Criar a Tabela:**
   - Garanta que a tabela seja criada na inicialização da aplicação.
     ```python
     # Adicionar em app/main.py
     from . import database, models
     models.Base.metadata.create_all(bind=database.engine)
     ```

**6. Implementar o `PayoutRepository` com SQLAlchemy:**
   - Reescreva o `app/repository.py` para usar a sessão do SQLAlchemy, tratando a `IntegrityError` para garantir a idempotência.
     ```python
     from sqlalchemy.orm import Session
     from sqlalchemy.exc import IntegrityError
     from . import models

     class PayoutRepository:
         def __init__(self, db_session: Session):
             self.db = db_session

         def was_processed(self, external_id: str) -> bool:
             """Verifica se um external_id já foi processado consultando o banco."""
             return self.db.query(models.PayoutDB).filter(models.PayoutDB.external_id == external_id).first() is not None

         def save_payout(self, payout: models.PayoutDetail) -> models.PayoutDetail:
             """
             Salva um Payout no banco. A idempotência é garantida pela
             constraint de unicidade na coluna `external_id`.
             """
             db_payout = models.PayoutDB(
                 external_id=payout.external_id,
                 status=payout.status,
                 amount_cents=payout.amount_cents
             )
             try:
                 self.db.add(db_payout)
                 self.db.commit()
                 self.db.refresh(db_payout)
                 return payout
             except IntegrityError:
                 self.db.rollback()
                 # Retorna um detalhe indicando duplicata
                 payout.status = "duplicate"
                 return payout
     ```

**7. Atualizar Testes (se necessário):**
   - Os testes unitários existentes para o repositório precisarão ser reescritos ou adaptados para mockar uma sessão de banco de dados, o que é mais complexo. Por agora, podemos remover `tests/test_repository.py` e focar nos testes de maior nível (serviço e E2E) nas próximas sagas.
     ```bash
     rm tests/test_repository.py
     ```

---

**Critério de Sucesso:**
1.  A aplicação deve iniciar com `docker compose up`, subindo os contêineres `api` e `db`.
2.  A tabela `payouts` deve ser criada no banco de dados Postgres.
3.  Os testes existentes (exceto o E2E) devem continuar passando.
