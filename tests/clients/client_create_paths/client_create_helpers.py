"""Helpers for the client_create_paths test (VCITA2-14007).

Migrated from automation-js:
  steps/desktop/clients.js (new-CRM create, CRM search)
  pages/desktop/Frontage/Clients/newClients.js + newClientDialog.js
  steps/desktop/businessPage.js + pages/desktop/Vitrage/livesite.js (livesite leave-details)
  steps/desktop/emails.js + api/email.js (email delivery via infra automation API)
  steps/desktop/conversations.js (client-portal conversation)

The CRM (`/app/clients`) is a POV Vue page with stable data-qa selectors. Email
delivery is verified through the same internal infra endpoint the legacy uses
(`/infra/automation/message/content`), authenticated with a directory token minted
from the isolated account's directory (admin `POST /platform/v1/tokens`).
"""

from __future__ import annotations

import os
import time

import requests
from playwright.sync_api import Page, expect

from tests import account_api

UI_TIMEOUT = 5000
CRM_PAGE_TIMEOUT = 15000
EMAIL_RETRIES = 30          # legacy api/email.js retries
EMAIL_INTERVAL_S = 3        # bounded poll interval for inbound-email eventual consistency
API_TIMEOUT = 30

# --- CRM (POV /app/clients) selectors (mirror legacy newClients.js) ---
# The CRM page (New button, search bar, table) is the top-level POV frame; the
# new-client dialog itself renders inside the nested Angular iframe.
NEW_BUTTON = '[data-qa="new-button"]'
NEW_CLIENT_OPTION = '[data-qa="more-actions-button_new_matter"]'
ANGULAR_IFRAME = 'iframe[name="angular-iframe"]'
DIALOG_FIRST = '[name="first_name"]'
DIALOG_LAST = '[name="last_name"]'
DIALOG_EMAIL = '[name="email"]'
DIALOG_SAVE = 'button:has-text("Save")'
SEARCH_ALL = '[data-qa="CrmTable-All-actionBar-searchBar"]'
ROW_NAME = (
    '[data-qa="CrmTable-All-item-matter_name"], '
    '[data-qa="CrmTable-All_mainClientName"], '
    '[data-qa="matter-name"]'
)
EMPTY_STATE = '[data-qa="VcEmptyState"]'


def app_base(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return base


# ---------------------------------------------------------------------------
# Email delivery (internal infra automation endpoint, directory-token auth)
# ---------------------------------------------------------------------------

def _directory_id(context: dict) -> str:
    directory_id = context.get("directory_id") or os.environ.get("VCITA_DIRECTORY_ID")
    if not directory_id:
        raise ValueError("directory_id missing from context and VCITA_DIRECTORY_ID unset")
    return directory_id


def _directory_token(context: dict) -> str:
    """Mint a directory token for the isolated account's directory (admin)."""
    cached = context.get("_cc_directory_token")
    if cached:
        return cached
    resp = requests.post(
        f"{account_api.resolve_api_base_url(context)}/platform/v1/tokens",
        json={"directory_id": _directory_id(context)},
        headers=account_api.admin_headers(),
        timeout=API_TIMEOUT,
    )
    resp.raise_for_status()
    data = (resp.json() or {}).get("data") or {}
    token = data.get("token")
    if not token:
        raise AssertionError(f"Directory token generation returned no token: {resp.text[:300]}")
    context["_cc_directory_token"] = token
    return token


def _fetch_account_emails(context: dict) -> list[dict]:
    resp = requests.get(
        f"{account_api.resolve_api_base_url(context)}/infra/automation/message/content",
        params={"business_uid": account_api.pivot_uid(context)},
        headers={"Authorization": f"Token {_directory_token(context)}"},
        timeout=API_TIMEOUT,
    )
    resp.raise_for_status()
    body = resp.json()
    return body if isinstance(body, list) else (body.get("data") or [])


def assert_email_with_subject(context: dict, subject: str, min_count: int = 1) -> dict:
    """Poll the infra automation endpoint until at least ``min_count`` emails with
    ``subject`` exist, returning the last match.

    Mirrors legacy api/email.js getEmailBySubject (bounded retries for the email
    pipeline's eventual consistency). ``min_count`` guards against vacuous re-asserts:
    when the same subject is sent by two channels (e.g. the client "Thank you for your
    message" for both livesite and widget), the second assertion must observe a *new*
    matching email rather than re-counting the first."""
    last_subjects: list[str] = []
    for _ in range(EMAIL_RETRIES):
        emails = _fetch_account_emails(context)
        matches = [e for e in emails if e.get("subject") == subject]
        if len(matches) >= min_count:
            return matches[-1]
        last_subjects = [e.get("subject") for e in emails]
        time.sleep(EMAIL_INTERVAL_S)
    raise AssertionError(
        f"Expected >= {min_count} email(s) with subject {subject!r} after "
        f"{EMAIL_RETRIES} polls. Seen subjects: {last_subjects}"
    )


# ---------------------------------------------------------------------------
# CRM (POV /app/clients): create via dialog + search
# ---------------------------------------------------------------------------

def open_crm(page: Page, context: dict) -> None:
    """Navigate to a fresh CRM client list. Always re-navigates: creating a client
    lands on its card, so a fresh load guarantees the list/search/table state."""
    page.goto(f"{app_base(context)}/app/clients", wait_until="domcontentloaded", timeout=CRM_PAGE_TIMEOUT)
    page.locator(NEW_BUTTON).first.wait_for(state="visible", timeout=CRM_PAGE_TIMEOUT)


def _find_dialog_frame(page: Page):
    """Return the frame hosting the new-client dialog (scans for #first_name).

    The dialog renders inside the nested Angular iframe; scanning page.frames for the
    form field is robust to the iframe's name/nesting."""
    deadline = time.monotonic() + CRM_PAGE_TIMEOUT / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(DIALOG_FIRST).count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError("New-client dialog (first_name) frame not found")


def crm_create_client(page: Page, context: dict, first: str, last: str, email: str) -> None:
    """Create a client through the new-CRM dialog (first/last/email + Save).

    Matches legacy NewClientDialog.createClient, which only fills first/last/email."""
    open_crm(page, context)
    page.locator(NEW_BUTTON).first.click()
    page.locator(NEW_CLIENT_OPTION).first.click(timeout=UI_TIMEOUT)
    frame = _find_dialog_frame(page)
    frame.locator(DIALOG_FIRST).first.wait_for(state="visible", timeout=CRM_PAGE_TIMEOUT)
    frame.locator(DIALOG_FIRST).first.fill(first, timeout=UI_TIMEOUT)
    frame.locator(DIALOG_LAST).first.fill(last, timeout=UI_TIMEOUT)
    frame.locator(DIALOG_EMAIL).first.fill(email, timeout=UI_TIMEOUT)
    frame.locator(DIALOG_SAVE).first.click(timeout=UI_TIMEOUT)
    frame.locator(DIALOG_FIRST).first.wait_for(state="hidden", timeout=CRM_PAGE_TIMEOUT)


def crm_search_assert(page: Page, context: dict, query: str, expected_name: str) -> None:
    """Search the CRM All tab and assert a row containing ``expected_name`` shows.

    The CRM search index is eventually consistent after creation, so the search is
    retried within a bounded budget until the expected row resolves."""
    open_crm(page, context)
    deadline = time.monotonic() + CRM_PAGE_TIMEOUT / 1000 * 3
    search = page.locator(SEARCH_ALL).first
    search.wait_for(state="visible", timeout=CRM_PAGE_TIMEOUT)
    while True:
        search.fill("", timeout=UI_TIMEOUT)
        search.fill(query, timeout=UI_TIMEOUT)
        page.wait_for_timeout(1500)
        rows = page.locator(ROW_NAME)
        texts = rows.all_inner_texts() if rows.count() else []
        if any(expected_name in t for t in texts):
            return
        if time.monotonic() >= deadline:
            raise AssertionError(
                f"CRM search {query!r} did not show a row containing {expected_name!r}. "
                f"Rows: {texts}"
            )
        page.wait_for_timeout(1500)
