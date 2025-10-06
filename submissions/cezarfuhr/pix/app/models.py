from pydantic import BaseModel, Field
from typing import List

class PayoutItem(BaseModel):
    external_id: str
    user_id: str
    amount_cents: int
    pix_key: str

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
