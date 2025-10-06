import os
os.environ['API_KEY'] = 'test-key'

from unittest.mock import Mock, patch
from app.services import PayoutService
from app.models import PayoutBatch, PayoutItem

def test_process_batch_with_duplicates():
    """Testa processamento de lote com duplicatas"""
    # Arrange
    mock_db_session = Mock()
    # Mock do repositorio que usa a sessao
    mock_repo = Mock()
    mock_repo.was_processed.side_effect = [True, False]

    # Injeta o mock do repositorio no servico
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

def test_process_batch_with_failures():
    """Testa processamento de lote com falhas"""
    # Arrange
    mock_db_session = Mock()
    mock_repo = Mock()
    mock_repo.was_processed.return_value = False

    with patch('app.services.PayoutRepository', return_value=mock_repo):
        service = PayoutService(db_session=mock_db_session)
        batch = PayoutBatch(
            batch_id="test-batch",
            items=[
                PayoutItem(external_id="fail-1", user_id="u1", amount_cents=100, pix_key="a"),
                PayoutItem(external_id="success-1", user_id="u2", amount_cents=200, pix_key="b"),
            ]
        )

        # Act - primeiro falha, segundo sucesso
        with patch.object(service, '_simulate_payment', side_effect=[False, True]):
            report = service.process_batch(batch)

    # Assert
    assert report.failed == 1
    assert report.successful == 1
    assert report.duplicates == 0
    assert mock_repo.save_payout.call_count == 1  # Apenas o sucesso foi salvo

def test_process_batch_all_successful():
    """Testa processamento de lote com todos sucessos"""
    # Arrange
    mock_db_session = Mock()
    mock_repo = Mock()
    mock_repo.was_processed.return_value = False

    with patch('app.services.PayoutRepository', return_value=mock_repo):
        service = PayoutService(db_session=mock_db_session)
        batch = PayoutBatch(
            batch_id="test-batch",
            items=[
                PayoutItem(external_id="item-1", user_id="u1", amount_cents=100, pix_key="a"),
                PayoutItem(external_id="item-2", user_id="u2", amount_cents=200, pix_key="b"),
                PayoutItem(external_id="item-3", user_id="u3", amount_cents=300, pix_key="c"),
            ]
        )

        # Act
        with patch.object(service, '_simulate_payment', return_value=True):
            report = service.process_batch(batch)

    # Assert
    assert report.successful == 3
    assert report.failed == 0
    assert report.duplicates == 0
    assert report.processed == 3
    assert len(report.details) == 3
    assert mock_repo.save_payout.call_count == 3
