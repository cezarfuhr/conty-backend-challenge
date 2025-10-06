### **Plano de Execução: Saga 04 - Serviço de Processamento**

**Objetivo:** Implementar a lógica de negócio no `PayoutService`, que orquestra o processamento do lote, utilizando o repositório com Postgres que agora garante a idempotência.

---

### **Passos de Execução**

**1. Refatorar o `PayoutService` em `app/services.py`:**
   - A lógica principal do serviço permanece a mesma, mas agora ele deve receber uma instância do `PayoutRepository` em seu construtor para interagir com o banco de dados.
   - Substitua o conteúdo de `app/services.py` por:
     ```python
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
             return random.random() < 0.95 # 95% de sucesso

         def process_batch(self, batch: PayoutBatch) -> PayoutReport:
             """Processa um lote de pagamentos, garantindo idempotência via DB."""
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
     ```

**2. Atualizar os Testes Unitários para o Serviço:**
   - Em `tests/test_services.py`, vamos adaptar os testes para mockar a sessão do banco de dados, em vez do repositório inteiro.
     ```python
     from unittest.mock import Mock, patch
     from app.services import PayoutService
     from app.models import PayoutBatch, PayoutItem

     def test_process_batch_with_duplicates():
         # Arrange
         mock_db_session = Mock()
         # Mock do repositório que usa a sessão
         mock_repo = Mock()
         mock_repo.was_processed.side_effect = [True, False]

         # Injeta o mock do repositório no serviço
         with patch('app.services.PayoutRepository', return_value=mock_repo):
             service = PayoutService(db_session=mock_db_session)
             batch = PayoutBatch(
                 batch_id="test-batch",
                 items=[
                     PayoutItem(external_id="dup-1", user_id="u1", amount_cents=100, pix_key="a"),
                     PayoutItem(external_id="new-1", user_id="u2", amount_cents=200, pix_key="b"),
                 ]
             )

             # Act
             with patch.object(service, '_simulate_payment', return_value=True):
                 report = service.process_batch(batch)

         # Assert
         assert report.duplicates == 1
         assert report.successful == 1
         mock_repo.save_payout.assert_called_once()

     # (O segundo teste, test_process_batch_with_failures, pode ser adaptado de forma similar)
     ```

---

**Critério de Sucesso:**
1.  O arquivo `app/services.py` deve ser atualizado com a nova lógica.
2.  Os testes em `tests/test_services.py` devem ser adaptados para mockar a dependência do banco de dados e devem passar.
3.  O teste E2E principal ainda deve falhar, pois a injeção de dependência na camada de API não está completa.
