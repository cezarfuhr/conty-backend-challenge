import os
os.environ['API_KEY'] = 'test-key'

import pytest
from pydantic import ValidationError
from app.models import PayoutItem, PayoutBatch


def test_payout_item_validates_positive_amount():
    """Garante que amount_cents deve ser positivo."""
    with pytest.raises(ValidationError) as exc_info:
        PayoutItem(
            external_id="test-1",
            user_id="u1",
            amount_cents=0,  # Invalido: deve ser > 0
            pix_key="user@test.com"
        )
    assert "greater than 0" in str(exc_info.value).lower()


def test_payout_item_validates_max_amount():
    """Garante que amount_cents nao excede o limite maximo."""
    with pytest.raises(ValidationError) as exc_info:
        PayoutItem(
            external_id="test-2",
            user_id="u1",
            amount_cents=200_000_000,  # Invalido: excede 100M
            pix_key="user@test.com"
        )
    assert "exceeds maximum" in str(exc_info.value).lower()


def test_payout_item_validates_empty_external_id():
    """Garante que external_id nao pode ser vazio."""
    with pytest.raises(ValidationError) as exc_info:
        PayoutItem(
            external_id="",  # Invalido: vazio
            user_id="u1",
            amount_cents=1000,
            pix_key="user@test.com"
        )
    assert "at least 1 character" in str(exc_info.value).lower()


def test_payout_item_strips_whitespace():
    """Garante que espacos em branco sao removidos automaticamente."""
    item = PayoutItem(
        external_id="  test-3  ",
        user_id="  u1  ",
        amount_cents=1000,
        pix_key="  user@test.com  "
    )
    assert item.external_id == "test-3"
    assert item.user_id == "u1"


def test_payout_batch_validates_empty_items():
    """Garante que batch deve ter pelo menos 1 item."""
    with pytest.raises(ValidationError) as exc_info:
        PayoutBatch(
            batch_id="batch-1",
            items=[]  # Invalido: vazio
        )
    assert "at least 1 item" in str(exc_info.value).lower()


def test_payout_item_accepts_valid_data():
    """Garante que dados validos sao aceitos."""
    item = PayoutItem(
        external_id="valid-id",
        user_id="user123",
        amount_cents=50000,
        pix_key="valid@pix.com"
    )
    assert item.external_id == "valid-id"
    assert item.amount_cents == 50000
