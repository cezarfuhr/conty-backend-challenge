from pydantic import BaseModel, Field, SecretStr
from typing import List
from sqlalchemy import Column, String, Integer, UniqueConstraint
from .database import Base

class PayoutItem(BaseModel):
    external_id: str
    user_id: str
    amount_cents: int
    pix_key: SecretStr

class PayoutBatch(BaseModel):
    batch_id: str
    items: List[PayoutItem]

class PayoutDetail(BaseModel):
    external_id: str
    status: str
    amount_cents: int

class PayoutReport(BaseModel):
    batch_id: str
    processed: int
    successful: int
    failed: int
    duplicates: int
    details: List[PayoutDetail]

class PayoutDB(Base):
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    status = Column(String)
    amount_cents = Column(Integer)
