from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from .core.config import settings
from .database import SessionLocal

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def validate_api_key(key: str = Security(api_key_header)):
    if not key or key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )

def get_db_session():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db:
            db.close()
