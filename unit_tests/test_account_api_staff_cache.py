"""Unit tests for the per-account owner-staff cache in tests.account_api.

Regression coverage for the isolated-account 500 ("undefined method `id' for
nil"): the first-staff uid must be re-resolved when the active account changes,
so a service created in a fresh isolated account never reuses a parent account's
staff uid.
"""

import tests.account_api as account_api


def _context(pivot: str) -> dict:
    return {"auto_account": {"pivot_uid": pivot, "api_token": "t"}}


def test_first_staff_uid_caches_per_account(monkeypatch):
    calls: list[str] = []

    def fake_request(context, method, path, **kwargs):
        calls.append(path)
        # The staff list is account-specific; echo the pivot into the uid.
        pivot = context["auto_account"]["pivot_uid"]
        return {"data": {"staff": [{"id": f"staff-{pivot}"}]}}

    monkeypatch.setattr(account_api, "account_request", fake_request)

    context = _context("acct-A")
    assert account_api.first_staff_uid(context) == "staff-acct-A"
    # Second call for the same account is served from cache (no extra request).
    assert account_api.first_staff_uid(context) == "staff-acct-A"
    assert len(calls) == 1


def test_first_staff_uid_refetches_when_account_changes(monkeypatch):
    def fake_request(context, method, path, **kwargs):
        pivot = context["auto_account"]["pivot_uid"]
        return {"data": {"staff": [{"id": f"staff-{pivot}"}]}}

    monkeypatch.setattr(account_api, "account_request", fake_request)

    context = _context("parent")
    assert account_api.first_staff_uid(context) == "staff-parent"

    # Simulate an isolated account swapping in while reusing the same context dict
    # (the parent cache must NOT leak into the isolated account).
    context["auto_account"]["pivot_uid"] = "isolated"
    assert account_api.first_staff_uid(context) == "staff-isolated"
