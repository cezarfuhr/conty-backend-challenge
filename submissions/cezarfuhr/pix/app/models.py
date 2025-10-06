from pydantic import BaseModel, Field, SecretStr, field_validator, ConfigDict
from typing import List
from sqlalchemy import Column, String, Integer, UniqueConstraint
from .database import Base

class PayoutItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    external_id: str = Field(..., min_length=1, max_length=255, description="Unique external identifier")
    user_id: str = Field(..., min_length=1, max_length=255, description="User identifier")
    amount_cents: int = Field(..., gt=0, description="Amount in cents (must be positive)")
    pix_key: SecretStr = Field(..., description="PIX key (masked for security)")

    @field_validator('amount_cents')
    @classmethod
    def validate_amount(cls, v: int) -> int:
        if v > 100_000_000:  # 1 milhao de reais
            raise ValueError('Amount exceeds maximum allowed (100,000,000 cents)')
        return v

class PayoutBatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    batch_id: str = Field(..., min_length=1, max_length=255, description="Batch identifier")
    items: List[PayoutItem] = Field(..., min_length=1, description="List of payout items (must have at least 1)")

class PayoutDetail(BaseModel):
    external_id: str
    status: str
    amount_cents: int

class PayoutReport(BaseModel):
    batch_id: str
    processed: int = Field(..., ge=0)
    successful: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)
    duplicates: int = Field(..., ge=0)
    details: List[PayoutDetail]

class PayoutDB(Base):
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    status = Column(String)
    amount_cents = Column(Integer)
