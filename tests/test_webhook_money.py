"""Monobank webhook: F2 (signature fail-open), F6 (replay double-credit),
F13 (raw exception leak).

The handler builds a real Bot(BOT_TOKEN); send_message is monkeypatched to a no-op
so no live Telegram user is ever messaged.
"""
import asyncio

import pytest

from conftest import QA_UID, char_col

CHAR_ID = 6
ORDER = "qa-test-invoice-0001"
CREDIT = 500


def _seed_payment(status=False):
    from conftest import _mysql
    _mysql(f"DELETE FROM money_payment WHERE order_id='{ORDER}'")
    _mysql(f"DELETE FROM payments WHERE order_id='{ORDER}'")
    _mysql(
        "INSERT INTO payments (order_id,user_id,price,created_time_payment,status) "
        f"VALUES ('{ORDER}',{QA_UID},{CREDIT},NOW(),{1 if status else 0})"
    )
    _mysql(
        "INSERT INTO money_payment (order_id,count_money) "
        f"VALUES ('{ORDER}',{CREDIT})"
    )


def _cleanup_payment():
    from conftest import _mysql
    _mysql(f"DELETE FROM money_payment WHERE order_id='{ORDER}'")
    _mysql(f"DELETE FROM payments WHERE order_id='{ORDER}'")


class _FakeReq:
    method = "POST"
    headers = {}


def _make_endpoint(monkeypatch):
    from webhook_api.handlers.money_handler import MonoResultMoney
    from webhook_api.schemas import MonoResultSchema

    async def noop(*a, **k):
        return None

    monkeypatch.setattr(MonoResultMoney, "bot", type("B", (), {"send_message": staticmethod(noop)})())
    ep = MonoResultMoney(_FakeReq())
    ep.data = MonoResultSchema(
        invoiceId=ORDER, status="success", amount=CREDIT * 100, ccy=980,
        createdDate="2026-07-25T00:00:00Z", modifiedDate="2026-07-25T00:00:00Z",
        reference="ref", destination="TG Football",
    )
    return ep


# ---- F2: signature verification fails open ----

@pytest.mark.asyncio
async def test_signature_fail_open(monkeypatch):
    import webhook_api.monobank_signature as sig

    monkeypatch.setattr(sig, "TOKEN_MONOBANK", "")
    ok = await sig.MonobankSignatureVerifier.verify(None, b'{"any":"body"}')
    assert ok is False, (
        "FAIL-OPEN: signature verification returned True with no merchant token; "
        "a forged callback would be accepted and credit real coins"
    )


@pytest.mark.asyncio
async def test_signature_rejects_bad_sign_when_configured(monkeypatch):
    import webhook_api.monobank_signature as sig

    monkeypatch.setattr(sig, "TOKEN_MONOBANK", "some-merchant-token")

    async def fake_pub():
        return b"-----BEGIN PUBLIC KEY-----\nnot-a-real-key\n-----END PUBLIC KEY-----"

    monkeypatch.setattr(sig.MonobankSignatureVerifier, "_get_pub_key_pem", classmethod(lambda cls: fake_pub()))
    ok = await sig.MonobankSignatureVerifier.verify("bad-sign", b'{"any":"body"}')
    assert ok is False


# ---- F6: replay double-credit ----

@pytest.mark.asyncio
async def test_replay_credits_exactly_once(monkeypatch):
    before = int(char_col(CHAR_ID, "money"))
    _seed_payment(status=False)
    try:
        # fire the same webhook twice concurrently
        ep1 = _make_endpoint(monkeypatch)
        ep2 = _make_endpoint(monkeypatch)
        await asyncio.gather(ep1.handle_request(), ep2.handle_request())
        after = int(char_col(CHAR_ID, "money"))
        assert after - before == CREDIT, (
            f"REPLAY DOUBLE-CREDIT: balance moved {after - before}, expected {CREDIT}"
        )
    finally:
        from conftest import _mysql
        _mysql(f"UPDATE characters SET money={before} WHERE id={CHAR_ID}")
        _cleanup_payment()


# ---- Atomicity: claim and credit must commit or roll back together ----

@pytest.mark.asyncio
async def test_claim_and_credit_are_one_transaction():
    """A failure while crediting must NOT leave the payment marked paid.

    Otherwise Monobank's retry sees status=True, credits nothing, and the player
    has paid for something they never received.
    """
    from services.payment_service import PaymentServise
    from conftest import scalar
    from sqlalchemy import update
    from database.models.character import Character

    before = int(char_col(CHAR_ID, "money"))
    _seed_payment(status=False)
    try:
        # second statement is invalid -> the whole transaction must roll back
        ok = await PaymentServise.claim_and_apply(
            ORDER,
            update(Character).where(Character.id == CHAR_ID).values(
                money=Character.money + CREDIT
            ),
            update(Character).where(Character.id == CHAR_ID).values(
                no_such_column_exists=1
            ),
        )
        status = scalar(f"SELECT status FROM payments WHERE order_id='{ORDER}'")
        after = int(char_col(CHAR_ID, "money"))
        assert str(status) == "0", (
            f"payment left marked paid ({status}) after a failed credit — money lost"
        )
        assert after == before, f"partial credit persisted: {before} -> {after}"
        assert ok is not True
    except Exception:
        # the failure surfaced to the caller; what matters is the DB state below
        status = scalar(f"SELECT status FROM payments WHERE order_id='{ORDER}'")
        after = int(char_col(CHAR_ID, "money"))
        assert str(status) == "0", f"payment left marked paid ({status}) after rollback"
        assert after == before, f"partial credit persisted: {before} -> {after}"
    finally:
        from conftest import _mysql
        _mysql(f"UPDATE characters SET money={before} WHERE id={CHAR_ID}")
        _cleanup_payment()


@pytest.mark.asyncio
async def test_claim_and_apply_credits_once_under_concurrency():
    """20 concurrent deliveries -> exactly one credit."""
    from services.payment_service import PaymentServise
    from sqlalchemy import update
    from database.models.character import Character

    before = int(char_col(CHAR_ID, "money"))
    _seed_payment(status=False)
    try:
        results = await asyncio.gather(*[
            PaymentServise.claim_and_apply(
                ORDER,
                update(Character).where(Character.id == CHAR_ID).values(
                    money=Character.money + CREDIT
                ),
            )
            for _ in range(20)
        ], return_exceptions=True)
        winners = sum(1 for r in results if r is True)
        after = int(char_col(CHAR_ID, "money"))
        assert winners == 1, f"{winners} deliveries credited, expected exactly 1"
        assert after - before == CREDIT, f"balance moved {after - before}, expected {CREDIT}"
    finally:
        from conftest import _mysql
        _mysql(f"UPDATE characters SET money={before} WHERE id={CHAR_ID}")
        _cleanup_payment()


# ---- F13: raw exception text leaked in webhook response ----

@pytest.mark.asyncio
async def test_error_response_has_no_raw_exception():
    from webhook_api.handlers.money_handler import MonoResultMoney
    import json as _json

    class _BadReq:
        method = "POST"
        headers = {}

        async def json(self):
            raise ValueError("secret-internal-detail-xyz")

    ep = MonoResultMoney(_BadReq())
    resp = await ep.get_data()
    body = resp.body.decode() if hasattr(resp, "body") else str(resp)
    assert "secret-internal-detail-xyz" not in body, (
        f"INFO LEAK: raw exception text returned to the client: {body[:200]}"
    )
