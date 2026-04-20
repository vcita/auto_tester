"""
Account factory for the test runner.

Creates and deletes business accounts via the vcita API.
Mirrors the auto_account pattern from automation-js:
  - Create: POST /platform/v1/businesses with directory token
  - Delete: GET /admin/users/{pivot_uid}/delete_business with admin token
  - List:   GET /platform/v1/businesses (admin API, paginated) filtered by email pattern
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Optional
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

AUTO_EMAIL_PATTERN = re.compile(r"^auto\.api\..+\.\d+@vcita\.com$")

DEFAULT_PASSWORD = "vcita123"
COUNTRY = "United States"
BUSINESSES_PATH = "/platform/v1/businesses"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 1
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


def load_directory_token(config: Optional[dict] = None) -> Optional[str]:
    """Load directory token from env var or config dict."""
    token = os.environ.get("VCITA_DIRECTORY_TOKEN")
    if token:
        return token
    if config:
        return (config.get("target") or {}).get("directory_token")
    return None


def load_admin_token(config: Optional[dict] = None) -> Optional[str]:
    """Load admin token from env var or config dict."""
    token = os.environ.get("VCITA_ADMIN_TOKEN")
    if token:
        return token
    if config:
        return (config.get("target") or {}).get("admin_token")
    return None


def create_account(api_base_url: str, directory_token: str, category_name: str) -> dict:
    """
    Create a business account for a single category.

    POST /platform/v1/businesses with directory token.

    Returns dict with: email, password, business_id, auth_token, name, pivot_uid, raw_response.
    Raises FatalTokenError on 401, AccountCreationError on other failures.
    """
    timestamp = int(time.time())
    email = f"auto.api.{category_name.lower()}.{timestamp}@vcita.com"
    business_name = f"Auto_{category_name}_{timestamp}"

    payload = {
        "admin_account": {
            "email": email,
            "password": DEFAULT_PASSWORD,
            "country_name": COUNTRY,
        },
        "business": {
            "name": business_name,
            "country_name": COUNTRY,
        },
        "meta": {},
    }

    url = f"{api_base_url.rstrip('/')}{BUSINESSES_PATH}"
    headers = {"Authorization": f"Token {directory_token}"}

    last_error = None
    for attempt in range(1 + MAX_RETRIES):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
            _handle_create_error(resp, category_name)
            data = resp.json()
            biz = data.get("data", {}).get("business", {})
            AccountLedger().record_created(email)
            admin_acct = biz.get("admin_account", {})
            # In the vcita API, business.id serves as both the business_id and the
            # pivot_uid used for account deletion (GET /admin/users/{pivot_uid}/delete_business).
            biz_id = biz.get("business", {}).get("id", "")
            return {
                "email": email,
                "password": DEFAULT_PASSWORD,
                "business_id": biz_id,
                "pivot_uid": biz_id,
                "user_id": admin_acct.get("user_id", "") or admin_acct.get("id", ""),
                "auth_token": biz.get("meta", {}).get("auth_token", ""),
                "name": business_name,
                "raw_response": data,
            }
        except FatalTokenError:
            raise
        except AccountCreationError:
            raise
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                logger.warning("Retry %d/%d for %s...", attempt + 1, MAX_RETRIES, category_name)
                time.sleep(RETRY_BACKOFF ** (attempt + 1))

    raise AccountCreationError(f"All retries exhausted for {category_name}: {last_error}")


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
                    cat_match = re.match(r"^auto\.api\.(.+)\.\d+@", email)
                    category = cat_match.group(1) if cat_match else "unknown"
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

    def __init__(self, ledger_dir: Optional['Path'] = None):
        from pathlib import Path
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
    """Extract the epoch timestamp from an auto.api email address."""
    match = re.search(r"\.(\d{10,})@", email)
    if match:
        return int(match.group(1))
    return None


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
            f"Set VCITA_DIRECTORY_TOKEN env var or target.directory_token in config.yaml. "
            f"Detail: {detail}"
        )

    if status in (400, 409):
        raise AccountCreationError(f"HTTP {status} for {category_name}: {detail}")

    if status >= 500:
        raise AccountCreationError(f"HTTP {status} server error for {category_name}: {detail}")

    resp.raise_for_status()
