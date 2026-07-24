"""Auth boundary: every malformed or foreign-signed initData must be rejected.

Covers finding F1 (TEST_BOT_TOKEN as a second valid signer = impersonate anyone)
and the initData freshness window (F12).
"""
import httpx
import pytest

from conftest import API, QA_UID, QA_UID_B, forge, hdr

ENDPOINT = f"{API}/api/player"


def test_health_is_open():
    r = httpx.get(f"{API}/api/health", timeout=10)
    assert r.status_code == 200 and r.json() == {"ok": True}


def test_valid_initdata_is_accepted(auth_qa):
    r = httpx.get(ENDPOINT, headers=auth_qa, timeout=10)
    assert r.status_code == 200, r.text


@pytest.mark.parametrize(
    "name,headers",
    [
        ("no_header", {}),
        ("empty_scheme", {"Authorization": ""}),
        ("wrong_scheme", {"Authorization": f"Bearer {forge(QA_UID)}"}),
        ("garbage", {"Authorization": "tma not-even-close"}),
        ("foreign_token", {"Authorization": f"tma {forge(QA_UID, token='1111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')}"}),
        ("stale_25h", {"Authorization": f"tma {forge(QA_UID, age_s=90000)}"}),
    ],
)
def test_rejected(name, headers):
    r = httpx.get(ENDPOINT, headers=headers, timeout=10)
    assert r.status_code == 401, f"{name}: expected 401, got {r.status_code} {r.text[:200]}"


def test_tampered_hash_rejected():
    init = forge(QA_UID)
    # flip the final hex digit of the signature
    last = init[-1]
    init = init[:-1] + ("0" if last != "0" else "1")
    r = httpx.get(ENDPOINT, headers=hdr(init), timeout=10)
    assert r.status_code == 401, r.text


def test_no_user_field_rejected():
    init = forge(QA_UID)
    stripped = "&".join(p for p in init.split("&") if not p.startswith("user="))
    r = httpx.get(ENDPOINT, headers=hdr(stripped), timeout=10)
    assert r.status_code == 401, r.text


def test_absent_user_gets_404_not_500(auth_qa):
    """A brand-new Telegram user must get a clean 404, never a stack trace."""
    from conftest import QA_UID_ABSENT

    r = httpx.get(ENDPOINT, headers=hdr(forge(QA_UID_ABSENT)), timeout=10)
    assert r.status_code == 404
    assert r.json() == {"detail": "No character"}


def test_test_bot_token_is_not_a_second_signer():
    """F1: if TEST_BOT_TOKEN is configured, anyone holding it can sign initData for
    ANY user id and the API accepts it. Prod must not accept a second signer.

    Skipped unless the API under test was started with TEST_BOT_TOKEN set, which is
    how the exploit is demonstrated (see qa-artifacts/VERIFICATION_REPORT.md).
    """
    token = os.environ.get("QA_EXPLOIT_TEST_BOT_TOKEN")
    if not token:
        pytest.skip("set QA_EXPLOIT_TEST_BOT_TOKEN to run the impersonation exploit")
    # Sign as the VICTIM using only the test-bot token.
    r = httpx.get(ENDPOINT, headers=hdr(forge(QA_UID_B, token=token)), timeout=10)
    assert r.status_code == 401, (
        "IMPERSONATION: test-bot token authenticated as another user "
        f"(status {r.status_code}, body {r.text[:200]})"
    )


import os  # noqa: E402
