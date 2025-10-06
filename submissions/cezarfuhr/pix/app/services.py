from sqlalchemy.orm import Session
from .models import PayoutBatch, PayoutReport
from .repository import PayoutRepository

class PayoutService:
    def __init__(self, db_session: Session):
        self.repository = PayoutRepository(db_session)

    def process_batch(self, batch: PayoutBatch) -> PayoutReport:
        # Logica a ser implementada na Saga 04.
        # Retorno hardcoded para o teste E2E falhar de forma previsivel.
        return PayoutReport(
            batch_id=batch.batch_id,
            processed=0,
            successful=0,
            failed=len(batch.items),
            duplicates=0,
            details=[]
        )
