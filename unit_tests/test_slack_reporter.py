from datetime import datetime, timedelta
from pathlib import Path

from src.runner.models import CategoryResult, RunResult, TestResult
from src.runner.slack_reporter import SlackReporter


def _run_result(*categories: CategoryResult) -> RunResult:
    start = datetime(2026, 6, 24, 12, 0, 0)
    return RunResult(
        started_at=start,
        completed_at=start + timedelta(seconds=42),
        category_results=list(categories),
    )


def _category(name: str, passed: int, failed: int) -> CategoryResult:
    results = [
        TestResult(
            test_name=f"{name}-{i}",
            test_path=Path(name),
            test_type="test",
            status="passed" if i < passed else "failed",
            duration_ms=1000,
        )
        for i in range(passed + failed)
    ]
    return CategoryResult(
        category_name=name, category_path=Path(name), test_results=results
    )


def test_disabled_when_no_webhook(monkeypatch):
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    reporter = SlackReporter()
    assert reporter.enabled is False
    # No webhook -> no-op, returns False, must not raise.
    assert reporter.post_summary(_run_result()) is False


def test_posts_when_webhook_set(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json

        class _Resp:
            ok = True
            status_code = 200
            text = "ok"

        return _Resp()

    monkeypatch.setattr("src.runner.slack_reporter.requests.post", fake_post)

    reporter = SlackReporter(webhook_url="https://hooks.slack.test/abc")
    result = _run_result(_category("invoices", passed=3, failed=1))
    assert reporter.post_summary(result, env="automation-aviv") is True

    assert captured["url"] == "https://hooks.slack.test/abc"
    text = captured["json"]["blocks"][0]["text"]["text"]
    assert "PARTIAL" in text  # 3 passed + 1 failed
    assert "automation-aviv" in text
    assert "`invoices`" in text  # failed category is listed


def test_post_failure_is_not_fatal(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr("src.runner.slack_reporter.requests.post", boom)
    reporter = SlackReporter(webhook_url="https://hooks.slack.test/abc")
    # Swallows the error and returns False rather than propagating.
    assert reporter.post_summary(_run_result()) is False
