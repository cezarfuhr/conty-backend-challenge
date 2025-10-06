from fastapi import FastAPI

app = FastAPI(title="Conty PIX Challenge")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok"}
