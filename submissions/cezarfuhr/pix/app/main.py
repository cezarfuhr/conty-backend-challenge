from fastapi import FastAPI
from app import api, database, models
from app.core.logging_config import configure_logging
from app.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Configura o logging como a primeira acao
configure_logging()

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Conty PIX Challenge")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"}
    )

app.include_router(api.router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok"}

@app.get("/health", tags=["Health Check"])
def health_check():
    """Rich health check with database connectivity and application info."""
    import time
    from sqlalchemy import text

    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "conty-pix-api",
        "version": "1.0.0",
        "checks": {
            "database": "unknown",
            "api": "healthy"
        }
    }

    # Check database connectivity
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_data["checks"]["database"] = "healthy"
    except Exception as e:
        health_data["status"] = "degraded"
        health_data["checks"]["database"] = f"unhealthy: {str(e)}"

    return health_data
