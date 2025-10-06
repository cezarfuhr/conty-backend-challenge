import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from .models import PayoutBatch, PayoutReport
from .services import PayoutService
from .dependencies import validate_api_key, get_db_session
from .limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/payouts/batch",
    response_model=PayoutReport,
    tags=["Payouts"],
    dependencies=[Depends(validate_api_key)]
)
@limiter.limit("5/minute")
def process_payout_batch(
    request: Request,
    batch: PayoutBatch,
    db: Session = Depends(get_db_session)
) -> PayoutReport:
    logger.info(f"Payout batch received: {batch.batch_id}")
    service = PayoutService(db_session=db)
    return service.process_batch(batch)
