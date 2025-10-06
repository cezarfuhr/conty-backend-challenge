from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .models import PayoutBatch, PayoutReport
from .services import PayoutService
from .dependencies import validate_api_key, get_db_session

router = APIRouter()

@router.post("/payouts/batch", response_model=PayoutReport, tags=["Payouts"])
def process_payout_batch(
    batch: PayoutBatch,
    db: Session = Depends(get_db_session),
    _api_key: None = Depends(validate_api_key)
) -> PayoutReport:
    service = PayoutService(db)
    return service.process_batch(batch)
