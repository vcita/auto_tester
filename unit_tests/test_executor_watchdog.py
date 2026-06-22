"""Regression tests for the per-test watchdog.

A single hung test (e.g. a corrupted browser context that never returns) must not
block the whole suite. The executor arms a SIGALRM itimer around each test and
converts an overrun into a normal failure so the runner can continue.
"""
import signal
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.runner.executor import (
    DEFAULT_WATCHDOG_SECONDS,
    WatchdogTimeout,
    _run_with_watchdog,
    _watchdog_seconds,
)
# Aliased so pytest does not try to collect the production class (name starts with "Test").
from src.runner.executor import TestExecutor as Executor


def test_fast_function_completes_normally():
    calls = []
    _run_with_watchdog(lambda page, ctx: calls.append((page, ctx)), "pg", {"k": "v"})
    assert calls == [("pg", {"k": "v"})]


def test_overrunning_function_is_force_failed(monkeypatch):
    monkeypatch.setenv("AUTO_TESTER_TEST_WATCHDOG_SECONDS", "1")
    with pytest.raises(WatchdogTimeout):
        _run_with_watchdog(lambda page, ctx: time.sleep(5), None, {})


def test_previous_sigalrm_handler_is_restored(monkeypatch):
    monkeypatch.setenv("AUTO_TESTER_TEST_WATCHDOG_SECONDS", "30")
    sentinel = signal.getsignal(signal.SIGALRM)
    _run_with_watchdog(lambda page, ctx: None, None, {})
    assert signal.getsignal(signal.SIGALRM) is sentinel
    # And the itimer is disarmed (no pending alarm left behind).
    assert signal.setitimer(signal.ITIMER_REAL, 0)[0] == 0


def test_disabled_watchdog_runs_unguarded(monkeypatch):
    monkeypatch.setenv("AUTO_TESTER_TEST_WATCHDOG_SECONDS", "0")
    done = []
    _run_with_watchdog(lambda page, ctx: done.append(time.sleep(0.2)), None, {})
    assert len(done) == 1


def test_watchdog_seconds_env_parsing(monkeypatch):
    monkeypatch.delenv("AUTO_TESTER_TEST_WATCHDOG_SECONDS", raising=False)
    assert _watchdog_seconds() == DEFAULT_WATCHDOG_SECONDS
    monkeypatch.setenv("AUTO_TESTER_TEST_WATCHDOG_SECONDS", "120")
    assert _watchdog_seconds() == 120
    monkeypatch.setenv("AUTO_TESTER_TEST_WATCHDOG_SECONDS", "not-a-number")
    assert _watchdog_seconds() == DEFAULT_WATCHDOG_SECONDS


def test_execute_returns_failed_on_hang(monkeypatch, tmp_path):
    monkeypatch.setenv("AUTO_TESTER_TEST_WATCHDOG_SECONDS", "1")
    test_dir = tmp_path / "hanging_test"
    test_dir.mkdir()
    (test_dir / "test.py").write_text(
        "import time\n\n\ndef test_hang(page, context):\n    time.sleep(10)\n"
    )

    executor = Executor(snapshots_dir=tmp_path / "shots")
    # Dummy page: the watchdog path must NOT touch the page (no screenshot on hang).
    result = executor.execute(test_dir, "test", SimpleNamespace(), {})

    assert result.status == "failed"
    assert result.error_type == "WatchdogTimeout"
    assert result.duration_ms < 5000
