import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .models import PayoutBatch, PayoutReport
from .services import PayoutService
from .dependencies import validate_api_key, get_db_session

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/payouts/batch",
    response_model=PayoutReport,
    tags=["Payouts"],
    dependencies=[Depends(validate_api_key)]
)
def process_payout_batch(
    batch: PayoutBatch,
    db: Session = Depends(get_db_session)
) -> PayoutReport:
    logger.info(f"Payout batch received: {batch.batch_id}")
    service = PayoutService(db_session=db)
    return service.process_batch(batch)
