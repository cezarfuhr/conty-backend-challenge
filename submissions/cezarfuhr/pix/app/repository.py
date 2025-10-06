from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models

class PayoutRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def was_processed(self, external_id: str) -> bool:
        """Verifica se um external_id ja foi processado consultando o banco."""
        return self.db.query(models.PayoutDB).filter(models.PayoutDB.external_id == external_id).first() is not None

    def save_payout(self, payout: models.PayoutDetail) -> models.PayoutDetail:
        """
        Salva um Payout no banco. A idempotencia e garantida pela
        constraint de unicidade na coluna `external_id`.
        """
        db_payout = models.PayoutDB(
            external_id=payout.external_id,
            status=payout.status,
            amount_cents=payout.amount_cents
        )
        try:
            self.db.add(db_payout)
            self.db.commit()
            self.db.refresh(db_payout)
            return payout
        except IntegrityError:
            self.db.rollback()
            # Retorna um detalhe indicando duplicata
            payout.status = "duplicate"
            return payout
