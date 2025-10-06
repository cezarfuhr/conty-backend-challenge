from .models import PayoutBatch, PayoutReport
from .repository import PayoutRepository

class PayoutService:
    def __init__(self):
        # Em uma aplicação real, injetaríamos a dependência.
        self.repository = PayoutRepository()

    def process_batch(self, batch: PayoutBatch) -> PayoutReport:
        # Lógica a ser implementada na Saga 04.
        # Retorno hardcoded para o teste E2E falhar de forma previsível.
        return PayoutReport(
            batch_id=batch.batch_id,
            processed=0,
            successful=0,
            failed=len(batch.items),
            duplicates=0,
            details=[]
        )
