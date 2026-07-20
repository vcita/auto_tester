from pathlib import Path

import pytest

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


def test_resolve_directory_id_known_env_uses_pinned_directory(monkeypatch):
    from src.runner import account_factory, env_config

    runner = Runner(Path("tests"))
    runner.env = "integration"
    runner.admin_token = "admin-token"
    # No explicit override -> the known env's pinned directory id is used and no
    # runtime discovery is attempted.
    monkeypatch.setattr(account_factory, "load_directory_id", lambda config: None)
    monkeypatch.setattr(
        account_factory,
        "discover_directory_id",
        lambda *a, **k: pytest.fail("discovery must not run for known envs"),
    )

    urls = env_config.resolve_urls("integration")
    assert runner._resolve_directory_id(None, urls) == "970"


def test_resolve_directory_id_feature_env_discovers_and_ignores_integration_env_var(monkeypatch):
    from src.runner import account_factory, env_config

    runner = Runner(Path("tests"))
    runner.env = "automation-aviv"
    runner.admin_token = "admin-token"
    runner.api_base_url = env_config.resolve_urls("automation-aviv")["api_base_url"]
    # The inherited integration VCITA_DIRECTORY_ID (970) must be ignored for a
    # feature env; the fenv's own directory is discovered at runtime.
    monkeypatch.setattr(account_factory, "load_directory_id", lambda config: "970")
    monkeypatch.setattr(account_factory, "discover_directory_id", lambda *a, **k: "15")

    urls = env_config.resolve_urls("automation-aviv")
    assert runner._resolve_directory_id(None, urls) == "15"


def test_resolve_directory_id_feature_env_falls_back_to_seed_default(monkeypatch):
    from src.runner import account_factory, env_config

    runner = Runner(Path("tests"))
    runner.env = "automation-aviv"
    runner.admin_token = "admin-token"
    runner.api_base_url = env_config.resolve_urls("automation-aviv")["api_base_url"]
    # Discovery returns nothing (transient failure) -> fall back to the seed
    # default from env_config, never abort.
    monkeypatch.setattr(account_factory, "discover_directory_id", lambda *a, **k: None)

    urls = env_config.resolve_urls("automation-aviv")
    assert runner._resolve_directory_id(None, urls) == env_config.FEATURE_ENV_DIRECTORY_ID
