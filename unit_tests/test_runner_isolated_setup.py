from pathlib import Path

import tests._functions.login.test as login_mod
from src.models import Category
from src.runner.runner import TestRunner as Runner

_PARENT_CONTEXT = {"username": "u", "password": "p", "base_url": "https://app.example.com"}


def test_path_targets_isolated_account_for_nested_isolated_subcategory():
    runner = Runner(Path("tests"))
    payments = Category(name="Payments", path=Path("payments"))
    invoices = Category(name="Invoices", path=Path("payments/invoices"))
    eu_strict = Category(
        name="EU Strict Invoices",
        path=Path("payments/invoices/eu_strict_invoices"),
        account_profile={"type": "isolated"},
    )

    assert runner._path_targets_isolated_account([payments, invoices, eu_strict]) is True


def test_path_targets_isolated_account_ignores_regular_subcategories():
    runner = Runner(Path("tests"))
    payments = Category(name="Payments", path=Path("payments"))
    invoices = Category(name="Invoices", path=Path("payments/invoices"))

    assert runner._path_targets_isolated_account([payments, invoices]) is False


def test_restore_parent_session_succeeds_without_flag(monkeypatch):
    runner = Runner(Path("tests"))
    monkeypatch.setattr(runner, "_clear_browser_session", lambda page: None)
    monkeypatch.setattr(login_mod, "fn_login", lambda *a, **k: None)

    assert runner._restore_parent_session(object(), _PARENT_CONTEXT) is True
    assert getattr(runner, "_parent_session_restore_failed", False) is False


def test_restore_parent_session_never_raises_and_flags_on_persistent_failure(monkeypatch):
    runner = Runner(Path("tests"))
    monkeypatch.setattr(runner, "_clear_browser_session", lambda page: None)

    def boom(*args, **kwargs):
        raise TimeoutError("Timeout 30000ms exceeded.")

    monkeypatch.setattr(login_mod, "fn_login", boom)

    # Runs in a finally block in production -- it must never propagate.
    assert runner._restore_parent_session(object(), _PARENT_CONTEXT) is False
    assert runner._parent_session_restore_failed is True


def test_restore_parent_session_retries_then_succeeds(monkeypatch):
    runner = Runner(Path("tests"))
    monkeypatch.setattr(runner, "_clear_browser_session", lambda page: None)
    attempts = {"count": 0}

    def flaky(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise TimeoutError("first attempt times out")

    monkeypatch.setattr(login_mod, "fn_login", flaky)

    assert runner._restore_parent_session(object(), _PARENT_CONTEXT) is True
    assert attempts["count"] == 2
    assert getattr(runner, "_parent_session_restore_failed", False) is False


def test_restore_parent_session_noops_without_credentials(monkeypatch):
    runner = Runner(Path("tests"))
    called = {"login": False}
    monkeypatch.setattr(login_mod, "fn_login", lambda *a, **k: called.__setitem__("login", True))

    # No username/password/base_url and no env-derived app_base_url -> nothing to do.
    assert runner._restore_parent_session(object(), {}) is True
    assert called["login"] is False
    assert getattr(runner, "_parent_session_restore_failed", False) is False
