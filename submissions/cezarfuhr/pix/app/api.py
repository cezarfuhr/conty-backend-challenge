from fastapi import APIRouter
from .models import PayoutBatch, PayoutReport
from .services import PayoutService

router = APIRouter()

@router.post("/payouts/batch", response_model=PayoutReport, tags=["Payouts"])
def process_payout_batch(batch: PayoutBatch) -> PayoutReport:
    service = PayoutService()
    return service.process_batch(batch)
