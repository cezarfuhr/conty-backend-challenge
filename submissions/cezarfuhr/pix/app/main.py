from fastapi import FastAPI
from app import api, database, models
from app.core.logging_config import configure_logging

# Configura o logging como a primeira acao
configure_logging()

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Conty PIX Challenge")

app.include_router(api.router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok"}
