import random
from typing import List
from sqlalchemy.orm import Session

from .models import PayoutBatch, PayoutReport, PayoutDetail
from .repository import PayoutRepository

class PayoutService:
    def __init__(self, db_session: Session):
        self.repository = PayoutRepository(db_session=db_session)

    def _simulate_payment(self) -> bool:
        """Simula a chamada a um provedor de pagamento externo."""
        return random.random() < 0.95  # 95% de sucesso

    def process_batch(self, batch: PayoutBatch) -> PayoutReport:
        """Processa um lote de pagamentos, garantindo idempotencia via DB."""
        report_details: List[PayoutDetail] = []
        successful_count = 0
        failed_count = 0
        duplicate_count = 0

        for item in batch.items:
            if self.repository.was_processed(item.external_id):
                duplicate_count += 1
                status = "duplicate"
            else:
                payment_succeeded = self._simulate_payment()
                if payment_succeeded:
                    successful_count += 1
                    status = "paid"
                    # Apenas marcamos como processado se o pagamento for um sucesso
                    payout_to_save = PayoutDetail(
                        external_id=item.external_id,
                        status=status,
                        amount_cents=item.amount_cents
                    )
                    self.repository.save_payout(payout_to_save)
                else:
                    failed_count += 1
                    status = "failed"

            report_details.append(
                PayoutDetail(
                    external_id=item.external_id,
                    status=status,
                    amount_cents=item.amount_cents
                )
            )

        return PayoutReport(
            batch_id=batch.batch_id,
            processed=successful_count + failed_count,
            successful=successful_count,
            failed=failed_count,
            duplicates=duplicate_count,
            details=report_details,
        )
