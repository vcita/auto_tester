"""
Slack reporter for the test runner.

Posts a concise pass/fail/duration summary of a completed run to a Slack
Incoming Webhook. This is the headless counterpart to CLIReporter.print_summary:
CronJobs running in feature envs have no terminal, so the run outcome is surfaced
to Slack instead.

Activation is opt-in and side-effect free by default: if SLACK_WEBHOOK_URL is not
set, post_summary is a no-op. This lets the reporter ship dormant and be enabled
later purely by injecting the webhook secret (see helm_chart externalSecret).
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import requests

from .models import RunResult

logger = logging.getLogger(__name__)

WEBHOOK_ENV_VAR = "SLACK_WEBHOOK_URL"
REQUEST_TIMEOUT = 10

# Emoji per overall run status, for an at-a-glance signal in the channel.
_STATUS_EMOJI = {
    "passed": ":white_check_mark:",
    "failed": ":x:",
    "partial": ":warning:",
}


class SlackReporter:
    """Posts a run summary to a Slack Incoming Webhook.

    Usage:
        SlackReporter().post_summary(result, env="automation-aviv")

    The webhook URL is read from the SLACK_WEBHOOK_URL env var (overridable via
    the constructor for tests). When absent, the reporter does nothing.
    """

    def __init__(self, webhook_url: Optional[str] = None):
        self._webhook_url = webhook_url or os.environ.get(WEBHOOK_ENV_VAR)

    @property
    def enabled(self) -> bool:
        return bool(self._webhook_url)

    def post_summary(
        self,
        result: RunResult,
        *,
        env: Optional[str] = None,
        selection: Optional[list[str]] = None,
    ) -> bool:
        """Post a summary of ``result`` to Slack.

        Args:
            result: the completed RunResult.
            env: the target env / namespace the suite ran against (for context).
            selection: optional list of categories/shards that were run.

        Returns:
            True if a message was posted, False if disabled or the post failed.
            Never raises -- a reporting failure must not fail the test run.
        """
        if not self.enabled:
            logger.debug("%s not set; skipping Slack summary.", WEBHOOK_ENV_VAR)
            return False

        try:
            payload = self._build_payload(result, env=env, selection=selection)
            resp = requests.post(
                self._webhook_url, json=payload, timeout=REQUEST_TIMEOUT
            )
            if not resp.ok:
                logger.warning(
                    "Slack summary post returned HTTP %d: %s",
                    resp.status_code,
                    resp.text[:200],
                )
                return False
            return True
        except Exception as exc:  # noqa: BLE001 - reporting must never be fatal
            logger.warning("Slack summary post failed: %s", exc)
            return False

    def _build_payload(
        self,
        result: RunResult,
        *,
        env: Optional[str],
        selection: Optional[list[str]],
    ) -> dict:
        status = result.status
        emoji = _STATUS_EMOJI.get(status, ":grey_question:")
        duration_s = result.duration_ms / 1000 if result.duration_ms else 0

        context_bits = []
        if env:
            context_bits.append(f"env `{env}`")
        if selection:
            context_bits.append(f"{len(selection)} categor{'y' if len(selection) == 1 else 'ies'}")
        context = " | ".join(context_bits)

        header = f"{emoji} Auto Tester run *{status.upper()}*"
        if context:
            header += f" — {context}"

        totals = (
            f"*{result.total_passed}* passed | "
            f"*{result.total_failed}* failed | "
            f"*{result.total_skipped}* skipped "
            f"(of {result.total_tests}) in {duration_s:.0f}s"
        )

        lines = [header, totals]

        # List failed/partial categories so failures are actionable without
        # digging into pod logs. Capped to keep the message readable.
        failed_cats = [
            c for c in result.category_results if c.status in ("failed", "partial")
        ]
        if failed_cats:
            shown = failed_cats[:10]
            detail = "\n".join(
                f"• `{c.category_name}` — {c.passed} passed, {c.failed} failed"
                for c in shown
            )
            if len(failed_cats) > len(shown):
                detail += f"\n• …and {len(failed_cats) - len(shown)} more"
            lines.append(detail)

        text = "\n".join(lines)
        return {
            "text": f"Auto Tester run {status.upper()}"
            + (f" ({env})" if env else ""),  # fallback/notification text
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": text},
                }
            ],
        }
