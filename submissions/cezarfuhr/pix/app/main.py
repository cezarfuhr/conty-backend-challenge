from fastapi import FastAPI
from app import api

app = FastAPI(title="Conty PIX Challenge")

app.include_router(api.router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok"}
