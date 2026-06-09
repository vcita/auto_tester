"""Helpers for the matter_deletion subcategory.

Migrated from automation-js (VCITA2-13990):
  steps/desktop/clients.js  -> "user deletes matter" (get_matter_uid + gotoMatter + deleteMatter)
  pages/desktop/Frontage/Clients/client.js -> deleteMatter (More -> "Delete client" -> ok())
  api/matters.js -> get_matter_uid

Matter navigation/frames reuse the matters_management page helpers; the only behavior
unique to this migration is resolving a matter uid via API and deleting the open matter
from the matter-detail ``More`` menu, so that is all that is defined here.
"""

import requests
from playwright.sync_api import Page

from tests.account_api import account_token, api_base
from tests.clients.matters_management.matters_helpers import (
    MATTER_TITLE,
    MORE_OPTION,
    OPEN_ATTEMPTS,
    UI_TIMEOUT,
    app_base,
    matter_frames,
)

REQUEST_TIMEOUT = 20

# More-menu "Delete client" item (outer Angular frame). Menu items render across
# Angular md-menu / Vuetify list variants, so match by text across them.
DELETE_MENU_SELECTOR = (
    "[role='menuitem']:has-text('Delete client'), "
    "button:has-text('Delete client'), "
    ".v-list-item__title:has-text('Delete client'), "
    "md-menu-item:has-text('Delete client')"
)
# Angular confirm dialog "ok()" button (legacy confirmDelete xpath).
CONFIRM_DELETE = "button[ng-click='ok()'][ng-disabled='shouldDisable()']"


def get_matter_uid(context: dict, contact_id: str, matter_name: str) -> str:
    """Resolve a matter's uid by display name (legacy api/matters.js get_matter_uid)."""
    response = requests.get(
        f"{api_base(context)}/business/clients/v1/contacts/{contact_id}/matters",
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    matters = (response.json().get("data") or {}).get("matters", [])
    for matter in matters:
        if matter.get("display_name") == matter_name:
            return matter["uid"]
    raise AssertionError(
        f"Matter {matter_name!r} not found under contact {contact_id}: "
        f"{[m.get('display_name') for m in matters]}"
    )


def _open_matter(page: Page, context: dict, contact_id: str, matter_uid: str):
    """Navigate to a specific matter (legacy gotoMatter: ?matter_uid=) and wait until ready.

    Bounded retry (1 + 2) absorbs transient integration load without any single wait
    exceeding the 5s cap.
    """
    url = f"{app_base(context)}/app/clients/{contact_id}?matter_uid={matter_uid}"
    last_error: Exception | None = None
    for attempt in range(OPEN_ATTEMPTS):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=UI_TIMEOUT)
        except Exception as error:
            last_error = error
        inner, outer = matter_frames(page)
        try:
            inner.locator(MATTER_TITLE).first.wait_for(state="visible", timeout=UI_TIMEOUT)
            return inner, outer
        except Exception as error:
            last_error = error
            print(f"    [open_matter] retry {attempt + 1}/{OPEN_ATTEMPTS}")
    raise AssertionError(f"Matter {matter_uid} did not become ready: {last_error}")


def delete_matter(page: Page, context: dict, contact_id: str, matter_name: str) -> None:
    """Delete `matter_name` under the contact via the matter-detail More menu.

    Mirrors legacy: resolve uid -> open the matter -> More -> "Delete client" -> confirm.
    Waits for the DELETE response so a follow-up navigation cannot abort the request.
    """
    matter_uid = get_matter_uid(context, contact_id, matter_name)
    _, outer = _open_matter(page, context, contact_id, matter_uid)

    more = outer.locator(MORE_OPTION).first
    more.wait_for(state="visible", timeout=UI_TIMEOUT)
    more.click()

    delete_item = outer.locator(DELETE_MENU_SELECTOR).first
    delete_item.wait_for(state="visible", timeout=UI_TIMEOUT)
    delete_item.click()

    confirm = outer.locator(CONFIRM_DELETE).first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    with page.expect_response(
        lambda response: response.request.method == "DELETE" and response.ok,
        timeout=UI_TIMEOUT * 2,
    ):
        confirm.evaluate("element => element.click()")
