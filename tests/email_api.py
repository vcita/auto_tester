"""Outbound-email verification helper (shared infra).

Mirrors the legacy automation-js ``api/email.js`` chain: the platform records every
message it would send to a business's clients and exposes them on an internal
automation endpoint. Tests assert a client received a given email by polling that
endpoint for a matching subject.

The endpoint resolves the business from a directory-scoped ``Token <directory_token>``
(it looks the business up under ``current_directory.businesses``); an Admin token has
no directory context and the call 500s with "undefined method `businesses' for nil".
So it is authenticated with the directory token of the directory auto_tester
provisions accounts on, keyed by ``context["directory_id"]`` (integration 970 /
production 16403, mirroring automation-js ``runtime/envs.js``). Override with the
``VCITA_DIRECTORY_TOKEN`` env var for other directories.

Email delivery is asynchronous/eventually consistent, so the lookups poll on a bounded
deadline (a documented exception to the 5s UI wait cap, same rationale as the legacy
30-retry loop).
"""

from __future__ import annotations

import os
import re
import time

from tests.account_api import account_request, pivot_uid, resolve_api_base_url

MESSAGE_CONTENT_PATH = "/infra/automation/message/content"

# Directory tokens for the automation directories (same values as automation-js
# runtime/envs.js). Keyed by the runner's resolved directory_id.
DIRECTORY_TOKENS = {
    "970": "ff333ad7960d32e873d48d5de772f826",  # integration (meet2know)
    "16403": "5e9a233cd00e628e57f0adc3a97bcb623aee75d0999557a3fbf9e040eeec753e",  # production
}
# Outbound email is eventually consistent; poll up to this bound (legacy used ~30
# retries / ~2min). Kept tighter since integration delivery is usually < 30s.
EMAIL_TIMEOUT_S = 90
EMAIL_POLL_INTERVAL_S = 2
URL_RE = re.compile(r"https?://[^\s\"'<>]+")


def _directory_headers(context: dict) -> dict:
    """Directory-token auth for the automation message endpoint.

    Prefers ``VCITA_DIRECTORY_TOKEN``; otherwise resolves by the run's
    ``directory_id``. The endpoint needs the directory context to find the business."""
    token = os.environ.get("VCITA_DIRECTORY_TOKEN")
    if not token:
        directory_id = str((context.get("directory_id") or "")).strip()
        token = DIRECTORY_TOKENS.get(directory_id)
    if not token:
        raise ValueError(
            "No directory token for the email endpoint: set VCITA_DIRECTORY_TOKEN or "
            f"add directory_id {context.get('directory_id')!r} to DIRECTORY_TOKENS"
        )
    return {"Authorization": f"Token {token}"}


def _fetch_emails(context: dict) -> list[dict]:
    """Return all recorded outbound emails for the account's business."""
    response = account_request(
        context,
        "GET",
        f"{MESSAGE_CONTENT_PATH}?business_uid={pivot_uid(context)}",
        base_url=resolve_api_base_url(context),
        headers=_directory_headers(context),
    )
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        data = response.get("data")
        if isinstance(data, list):
            return data
        return response.get("messages") or response.get("emails") or []
    return []


def wait_for_email(context: dict, subject: str, timeout_s: int = EMAIL_TIMEOUT_S,
                   *, match: str = "exact") -> dict:
    """Poll the outbound-email log until an email matching ``subject`` appears.

    ``match`` selects how ``subject`` is compared against each recorded email:
    - ``"exact"`` (default): the subject equals ``subject`` (static subjects like
      "Payment Confirmation").
    - ``"prefix"``: the subject starts with ``subject``. Used for the
      "<verb> from <business>" subjects whose business-name suffix is dynamic on
      auto_tester isolated accounts (``Auto_<category>_<ts>``), so only the stable
      prefix ("New payment request from ", ...) is asserted.

    Returns the matching email dict (carries ``subject`` and ``text_part``). Raises with
    the subjects actually seen so a missing email is easy to diagnose."""
    deadline = time.monotonic() + timeout_s
    seen: list[str] = []
    while time.monotonic() < deadline:
        emails = _fetch_emails(context)
        seen = [e.get("subject", "") for e in emails if isinstance(e, dict)]
        for email in emails:
            if isinstance(email, dict) and _subject_matches(email.get("subject", ""), subject, match):
                return email
        time.sleep(EMAIL_POLL_INTERVAL_S)
    raise AssertionError(
        f"No email with subject {match} {subject!r} after {timeout_s}s "
        f"(saw subjects: {seen[-10:]})"
    )


def _subject_matches(actual: str | None, subject: str, match: str) -> bool:
    actual = actual or ""  # some recorded messages have a null subject
    return actual.startswith(subject) if match == "prefix" else actual == subject


def emails_matching(context: dict, subject: str, *, match: str = "exact") -> list[dict]:
    """Return all recorded outbound emails whose subject matches ``subject``."""
    return [
        email for email in _fetch_emails(context)
        if isinstance(email, dict) and _subject_matches(email.get("subject", ""), subject, match)
    ]


def wait_for_email_count(context: dict, subject: str, min_count: int,
                         timeout_s: int = EMAIL_TIMEOUT_S, *, match: str = "exact") -> list[dict]:
    """Poll until at least ``min_count`` emails matching ``subject`` exist; return them.

    Used when an action is expected to send another copy of the same subject (e.g. a
    second payment-request link or a second payment confirmation), so each repeated
    action is verified by the email count growing rather than re-matching the first."""
    deadline = time.monotonic() + timeout_s
    matches: list[dict] = []
    seen: list[str] = []
    while time.monotonic() < deadline:
        emails = _fetch_emails(context)
        seen = [e.get("subject", "") for e in emails if isinstance(e, dict)]
        matches = [e for e in emails if isinstance(e, dict)
                   and _subject_matches(e.get("subject", ""), subject, match)]
        if len(matches) >= min_count:
            return matches
        time.sleep(EMAIL_POLL_INTERVAL_S)
    raise AssertionError(
        f"Expected >= {min_count} emails with subject {match} {subject!r} after {timeout_s}s "
        f"(found {len(matches)}; saw subjects: {seen[-10:]})"
    )


def email_link(email: dict) -> str:
    """Extract the first http(s) URL from an email body (mirrors legacy CP-from-email)."""
    match = URL_RE.search(email.get("text_part") or email.get("html_part") or "")
    if not match:
        raise AssertionError(f"No URL found in email body for subject {email.get('subject')!r}")
    return match.group(0)
