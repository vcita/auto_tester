"""
Account factory for the test runner.

Creates and deletes business accounts via the vcita API.
Mirrors the automatic-account path from automation-js:
  - Create: POST /admin/users/ with admin token and Platinum package
  - Delete: GET /admin/users/{pivot_uid}/delete_business with admin token
  - List:   GET /platform/v1/businesses (admin API, paginated) filtered by email pattern
"""

from __future__ import annotations

import logging
import json
import os
import re
import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

AUTO_EMAIL_PATTERN = re.compile(r"^auto\..+\.\d+@vcita\.com$")

DEFAULT_PASSWORD = "vcita123"
COUNTRY = "United States"
# Pin the business timezone to match the browser context (runner uses
# timezone_id='America/New_York'). Without this the directory defaults new US
# businesses to Central Time, creating a 1h Central-vs-Eastern gap that drifts
# every calendar time assertion. Aligning both ends makes rendered times
# deterministic.
DEFAULT_TIME_ZONE = "Eastern Time (US & Canada)"
BUSINESSES_PATH = "/platform/v1/businesses"
ADMIN_USERS_PATH = "/admin/users/"
PLATINUM_PACKAGE_SUBSCRIPTION_ID = 14
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2
RETRY_BACKOFF = 2

AUTOMATION_FEATURE_FLAGS = [
    "hide_register_wizard",
    "hide_payment_success_message",
    "hide_first_event_success_message",
    "hide_empty_state",
]


class FatalTokenError(Exception):
    """Raised on 401 -- token is invalid or expired. Abort the entire run."""


class AccountCreationError(Exception):
    """Raised when account creation fails for a single category (non-fatal)."""


def load_admin_token(config: Optional[dict] = None) -> Optional[str]:
    """Load admin token from env var or config dict."""
    token = os.environ.get("VCITA_ADMIN_TOKEN")
    if token:
        return token
    if config:
        return (config.get("target") or {}).get("admin_token")
    return None


def load_directory_id(config: Optional[dict] = None) -> Optional[str]:
    """Load directory id from env var or config dict."""
    directory_id = os.environ.get("VCITA_DIRECTORY_ID")
    if directory_id:
        return directory_id
    if config:
        return (config.get("target") or {}).get("directory_id")
    return None


def create_account(
    api_base_url: str,
    admin_token: str,
    directory_id: str,
    category_name: str,
    country_name: str = COUNTRY,
) -> dict:
    """
    Create a business account for a single category.

    POST /admin/users/ with admin token.

    Returns dict with: email, password, business_id, auth_token, name, pivot_uid, raw_response.
    Raises FatalTokenError on 401, AccountCreationError on other failures.
    """
    timestamp = int(time.time())
    email = build_auto_email(category_name, timestamp)
    business_name = f"Auto_{normalize_email_category(category_name)}_{timestamp}"

    options = {
        "email": email,
        "business_name": business_name,
        "password": DEFAULT_PASSWORD,
        "directory_id": directory_id,
        "country_name": country_name,
        "time_zone": DEFAULT_TIME_ZONE,
        "package_subscription_id": PLATINUM_PACKAGE_SUBSCRIPTION_ID,
    }
    payload = {"generate_api_token": True, "options": json.dumps(options)}

    url = f"{api_base_url.rstrip('/')}{ADMIN_USERS_PATH}"
    headers = {"Authorization": f"Admin {admin_token}"}

    last_error = None
    for attempt in range(1 + MAX_RETRIES):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
            _handle_create_error(resp, category_name)
            data = resp.json()
            AccountLedger().record_created(email)
            account = _normalize_created_account(data, email, business_name)
            _ensure_business_timezone(api_base_url, admin_token, account.get("pivot_uid"))
            return account
        except FatalTokenError:
            raise
        except AccountCreationError as exc:
            last_error = exc
            if _is_retryable_create_error(exc) and attempt < MAX_RETRIES:
                logger.warning(
                    "Retry %d/%d for %s after transient create error...",
                    attempt + 1,
                    MAX_RETRIES,
                    category_name,
                )
                time.sleep(RETRY_BACKOFF ** (attempt + 1))
                continue
            raise
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                logger.warning("Retry %d/%d for %s...", attempt + 1, MAX_RETRIES, category_name)
                time.sleep(RETRY_BACKOFF ** (attempt + 1))

    raise AccountCreationError(f"All retries exhausted for {category_name}: {last_error}")


def build_auto_email(category_name: str, timestamp: Optional[int] = None) -> str:
    account_timestamp = timestamp if timestamp is not None else int(time.time())
    safe_category = normalize_email_category(category_name)
    return f"auto.{safe_category}.{account_timestamp}@vcita.com"


def normalize_email_category(category_name: str) -> str:
    """Convert category names to an email-safe segment."""
    normalized = re.sub(r"[^a-z0-9-]+", "-", category_name.lower()).strip("-")
    return normalized or "category"


def set_automation_feature_flags(
    api_base_url: str, admin_token: str, user_id: str
) -> bool:
    """Enable automation feature flags (hide wizard, etc.) on a freshly created account."""
    url = f"{api_base_url.rstrip('/')}/admin/feature_flags/{user_id}/add_user_features"
    headers = {"Authorization": f"Admin {admin_token}"}
    features = ",".join(AUTOMATION_FEATURE_FLAGS)
    try:
        resp = requests.post(url, json={"features": features}, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.ok:
            return True
        logger.warning("Set feature flags for %s returned HTTP %d: %s", user_id, resp.status_code, resp.text[:200])
        return False
    except Exception as exc:
        logger.warning("Set feature flags for %s failed: %s", user_id, exc)
        return False


def update_account_country(
    api_base_url: str, admin_token: str, pivot_uid: str, country_name: str
) -> None:
    """Update a business country after feature flags are active."""
    url = f"{api_base_url.rstrip('/')}/platform/v1/businesses/{pivot_uid}"
    headers = {"Authorization": f"Admin {admin_token}"}
    payload = {
        "business": {
            "business": {
                "country_name": country_name,
            },
        },
    }
    response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
    if not response.ok:
        raise AccountCreationError(
            f"Failed to update country for {pivot_uid} to {country_name}: "
            f"HTTP {response.status_code} {response.text[:300]}"
        )


def _ensure_business_timezone(
    api_base_url: str, admin_token: str, pivot_uid: Optional[str]
) -> None:
    """Force the business timezone to match the pinned browser timezone.

    Best-effort: the create call already passes ``time_zone`` in options, but some
    directories ignore it and fall back to Central. This authoritative update keeps
    rendered calendar times deterministic. Failures are logged, not fatal.
    """
    if not pivot_uid:
        return
    url = f"{api_base_url.rstrip('/')}/platform/v1/businesses/{pivot_uid}"
    headers = {"Authorization": f"Admin {admin_token}"}
    payload = {"business": {"business": {"time_zone": DEFAULT_TIME_ZONE}}}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        if not response.ok:
            logger.warning(
                "Failed to set timezone for %s: HTTP %d %s",
                pivot_uid, response.status_code, response.text[:200],
            )
    except Exception as exc:
        logger.warning("Failed to set timezone for %s: %s", pivot_uid, exc)


def delete_account(
    api_base_url: str, admin_token: str, pivot_uid: str, email: Optional[str] = None
) -> bool:
    """
    Delete a business account.

    GET /admin/users/{pivot_uid}/delete_business with admin token.
    If email is provided, also removes the email from the local ledger.
    Returns True on success, False on failure (logs warning).
    """
    url = f"{api_base_url.rstrip('/')}/admin/users/{pivot_uid}/delete_business"
    headers = {"Authorization": f"Admin {admin_token}"}

    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.ok or resp.status_code == 404:
            if email:
                AccountLedger().mark_deleted(email)
            return True
        logger.warning("Delete account %s returned HTTP %d: %s", pivot_uid, resp.status_code, resp.text[:200])
        return False
    except Exception as exc:
        logger.warning("Delete account %s failed: %s", pivot_uid, exc)
        return False


def list_auto_accounts(api_base_url: str, admin_token: str) -> list[dict]:
    """
    Find automation-created accounts by looking up emails recorded in the local ledger.

    The admin API only supports exact-email lookup (GET /platform/v1/businesses?email=X),
    so we maintain a lightweight ledger of created emails and verify each against the API.

    Returns list of dicts: {pivot_uid, email, name} for accounts that still exist.
    """
    ledger = AccountLedger()
    active_emails = ledger.get_active_emails()

    if not active_emails:
        return []

    headers = {"Authorization": f"Admin {admin_token}"}
    base_url = api_base_url.rstrip("/")
    accounts: list[dict] = []

    for email in active_emails:
        try:
            encoded = quote(email, safe="")
            resp = requests.get(
                f"{base_url}{BUSINESSES_PATH}?email={encoded}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.ok:
                uids = resp.json().get("data", {}).get("businesses", [])
                if uids:
                    ts = parse_email_timestamp(email)
                    category = parse_email_category(email) or "unknown"
                    accounts.append({
                        "pivot_uid": uids[0],
                        "email": email,
                        "name": f"Auto_{category}_{ts or '?'}",
                    })
                else:
                    ledger.mark_deleted(email)
            elif resp.status_code == 400:
                ledger.mark_deleted(email)
        except Exception as exc:
            logger.warning("Lookup %s failed: %s", email, exc)

    return accounts


class AccountLedger:
    """
    Lightweight local ledger tracking emails of auto-created accounts.

    Stored at .accounts/ledger.json (relative to project root). Each entry is an email string.
    The ledger is append-only during creation and entries are removed
    when deletion is confirmed (either explicitly or via API 404).

    This is intentionally minimal -- just a list of email strings.
    The source of truth for whether an account exists is the live API;
    the ledger is just an index to know which emails to look up.

    NOTE: The read-modify-write cycle is not atomic. Concurrent runners
    (e.g. parallel CI jobs) can overwrite each other's changes.
    TODO: Add file locking if concurrent execution becomes a use case.
    """

    def __init__(self, ledger_dir: Optional[Path] = None):
        self._dir = ledger_dir or Path(__file__).resolve().parents[2] / ".accounts"
        self._path = self._dir / "ledger.json"

    def record_created(self, email: str) -> None:
        entries = self._load()
        if email not in entries:
            entries.append(email)
            self._save(entries)

    def mark_deleted(self, email: str) -> None:
        entries = self._load()
        if email in entries:
            entries.remove(email)
            self._save(entries)

    def get_active_emails(self) -> list[str]:
        return self._load()

    def _load(self) -> list[str]:
        import json
        if not self._path.exists():
            return []
        try:
            with open(self._path, "r") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save(self, entries: list[str]) -> None:
        import json
        self._dir.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(entries, f, indent=2)


def parse_email_timestamp(email: str) -> Optional[int]:
    """Extract the epoch timestamp from an auto account email address."""
    match = re.search(r"\.(\d{10,})@", email)
    if match:
        return int(match.group(1))
    return None


def parse_email_category(email: str) -> Optional[str]:
    """Extract category from auto account email format."""
    match = re.match(r"^auto\.(.+)\.\d+@", email)
    return match.group(1) if match else None


def _normalize_created_account(data: dict, email: str, business_name: str) -> dict:
    """Normalize admin account creation responses to the runner account shape."""
    response_data = data.get("data", data)
    business = response_data.get("business", {})
    admin_account = response_data.get("admin_account", {})
    meta = response_data.get("meta", {})

    pivot_uid = (
        response_data.get("pivot_uid")
        or response_data.get("business_id")
        or business.get("pivot_uid")
        or business.get("id")
        or ""
    )
    user_id = (
        response_data.get("user_id")
        or admin_account.get("user_id")
        or admin_account.get("id")
        or ""
    )
    auth_token = (
        response_data.get("auth_token")
        or response_data.get("api_token")
        or meta.get("auth_token")
        or meta.get("api_token")
        or ""
    )

    return {
        "email": email,
        "password": DEFAULT_PASSWORD,
        "business_id": pivot_uid,
        "pivot_uid": pivot_uid,
        "user_id": user_id,
        "auth_token": auth_token,
        "api_token": auth_token,
        "name": business_name,
        "raw_response": data,
    }


def _handle_create_error(resp: requests.Response, category_name: str) -> None:
    if resp.ok:
        return

    status = resp.status_code
    try:
        body = resp.json()
    except Exception:
        body = {"message": resp.text[:500]}

    detail = body.get("message") or body.get("data") or resp.text[:300]

    if status == 401:
        raise FatalTokenError(
            f"401 Unauthorized — token is invalid or expired. "
            f"Set VCITA_ADMIN_TOKEN env var or target.admin_token in config.yaml. "
            f"Detail: {detail}"
        )

    if status in (400, 409):
        raise AccountCreationError(f"HTTP {status} for {category_name}: {detail}")

    if status == 403:
        raise AccountCreationError(f"HTTP {status} transient forbidden for {category_name}: {detail}")

    if status >= 500:
        raise AccountCreationError(f"HTTP {status} server error for {category_name}: {detail}")

    resp.raise_for_status()


def _is_retryable_create_error(exc: AccountCreationError) -> bool:
    error = str(exc).lower()
    return "server error" in error or "transient forbidden" in error
