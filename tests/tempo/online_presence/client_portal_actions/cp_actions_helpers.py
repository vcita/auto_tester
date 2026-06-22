"""UI helpers for the client_portal_actions test (VCITA2-14060).

Migrated from automation-js:
  steps/desktop/clientPortalSettings.js (add/edit/hide/show/delete actions)
  pages/desktop/Frontage/clientPortalSettings.js (ClientPortalSettings page object)
  steps/desktop/clientPortal.js (client portal displays/doesn't display actions)
  pages/desktop/ClientPortal/dashboard.js (getActionListFromCP)

Frame topology (POV):
- The Client Portal editor renders the legacy Frontage page inside nested iframes:
    page -> iframe[title="angularjs"] (outer/Angular) -> #vue_iframe_layout (inner/Vue).
  The "Edit portal" action button and the action edit dialog (button-text input +
  Save) live in the outer Angular frame (legacy `switchToPageContext`); the action
  canvas (Add action, the per-action menu, Done) lives in the inner Vue frame
  (legacy `switchToiFrame(vue_iframe_layout, ...)`). This mirrors contact_form_helpers.
- The client portal livesite is a separate browser context opened as the client
  (`/site/{uid}/action?client_jwt=<token>`); the action buttons render inside the
  `#cp_iframe` (mirrors estimates_helpers.open_cp_estimate_page).

The editor renders the same on the autotester default directory (970); the only
care needed is the Edit-portal click, which drives an Angular -> Vue iframe reload
and is flaky on a single click — `_enter_edit_mode` retries it within NAV_TIMEOUT.

All element waits are capped at 5s (UI_TIMEOUT); CP livesite navigation/cache lag
is bounded by CP_SETTLE (eventual consistency only, not a fixed sleep).
"""

from __future__ import annotations

import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from tests.account_api import pivot_uid

UI_TIMEOUT = 5_000
NAV_TIMEOUT = 20_000  # Angular/Vue iframe (re)load points; conditional, not a fixed sleep
CP_LOAD_TIMEOUT = 15_000  # per-attempt wait for the CP livesite to render its actions
CP_SETTLE = 60  # seconds; bounded budget for the CP cache + cold-load to settle (allows retries)

OUTER_IFRAME = 'iframe[title="angularjs"]'
INNER_IFRAME = "#vue_iframe_layout"

# Client Portal editor (outer Angular frame)
EDIT_PORTAL_BTN = '[data-qa="action-button-livesite-edit_portal"]'
BUTTON_TEXT_INPUT = 'input[ng-model*="action.title"]'
SAVE_BTN = "//button[contains(., 'Save')]"

# Editor canvas (inner Vue frame)
ADD_ACTION = ".add-action-text"
ACTION_CONTAINER = ".item-container"
ACTION_TITLE = ".action__title"
ACTION_MENU = ".action-item"
DONE_BTN = '[data-qa="dialog-submit-button"]'

# Client Portal livesite (separate client context)
CP_IFRAME = "#cp_iframe"
QUICK_ACTIONS = ".quick-actions"
QUICK_ACTION = ".layout.quick-action"

# Per-action menu items keyed by intent (legacy `performAction` mode map)
_SUB_ACTION = {"hide": "toggleHide", "show": "toggleHide", "delete": "deleteItem", "edit": "openEditItem"}


def _app_base(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return base


def _vitrage_base(context: dict) -> str:
    """Public Vitrage livesite base derived from the account's app base_url, matching
    the convention used across autotester (estimates_helpers, client_create_channels):
    app.meet2know -> live.meet2know, app.vcita -> live.vcita, fenv app-... -> vitrage-...."""
    base = _app_base(context)
    if "app.meet2know.com" in base:
        return "https://live.meet2know.com"
    if "app.vcita.com" in base:
        return "https://live.vcita.com"
    if "app-" in base and ".external.int-eks.vchost.co" in base:
        return base.replace("https://app-", "https://vitrage-", 1)
    raise ValueError(f"Cannot derive vitrage base URL from base_url={base!r}")


def _frames(page: Page):
    """Return (inner Vue frame_locator, outer Angular frame_locator)."""
    outer = page.frame_locator(OUTER_IFRAME)
    inner = outer.frame_locator(INNER_IFRAME)
    return inner, outer


def open_editor(page: Page, context: dict) -> None:
    """Navigate to the Client Portal editor and wait for the Edit-portal control."""
    page.goto(
        f"{_app_base(context)}/app/client-portal-editor",
        wait_until="domcontentloaded",
        timeout=NAV_TIMEOUT,
    )
    _, outer = _frames(page)
    outer.locator(EDIT_PORTAL_BTN).first.wait_for(state="visible", timeout=NAV_TIMEOUT)


def _enter_edit_mode(page: Page):
    """Click Edit portal and return the (inner, outer) frames with the canvas ready.

    The Edit-portal button drives an Angular -> Vue iframe (re)load. A single click
    is flaky: it can land before Angular attaches its handler, or the inner Vue
    canvas can take longer than one wait interval to render. So poll within the
    NAV_TIMEOUT budget — re-clicking the button each interval until the Add-action
    control becomes visible (and short-circuiting if we're already in edit mode)."""
    inner, outer = _frames(page)
    add_action_el = inner.locator(ADD_ACTION).first
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while True:
        if add_action_el.is_visible():
            return inner, outer
        edit_btn = outer.locator(EDIT_PORTAL_BTN).first
        try:
            if edit_btn.is_visible():
                edit_btn.click(timeout=UI_TIMEOUT)
        except Exception:
            pass  # button may detach mid-transition; the wait below retries
        try:
            add_action_el.wait_for(state="visible", timeout=UI_TIMEOUT)
            return inner, outer
        except Exception:
            if time.monotonic() >= deadline:
                raise AssertionError(
                    "Edit-portal editor canvas did not open within budget"
                )


def _save_edit_dialog(page: Page, inner) -> None:
    """Save the action edit dialog (outer frame) and confirm with Done (inner frame)."""
    _, outer = _frames(page)
    outer.locator(f"xpath={SAVE_BTN}").first.click(timeout=UI_TIMEOUT)
    done = inner.locator(DONE_BTN).first
    done.wait_for(state="visible", timeout=UI_TIMEOUT)
    done.click(timeout=UI_TIMEOUT)
    done.wait_for(state="detached", timeout=NAV_TIMEOUT)


def add_action(page: Page, context: dict, action_type: str, button_text: str) -> None:
    """Add a Client Portal action (e.g. 'Contact us') with the given button text."""
    inner, outer = _enter_edit_mode(page)
    inner.locator(ADD_ACTION).first.click(timeout=UI_TIMEOUT)
    inner.locator(
        f"xpath=//div[contains(@id,'list-item')]//div[contains(., '{action_type}')]"
    ).first.click(timeout=UI_TIMEOUT)
    title = outer.locator(BUTTON_TEXT_INPUT).first
    title.wait_for(state="visible", timeout=UI_TIMEOUT)
    title.fill(button_text, timeout=UI_TIMEOUT)
    _save_edit_dialog(page, inner)


def _open_action_menu(inner, button_text: str, intent: str):
    """Open the per-action kebab menu for ``button_text`` and click its ``intent`` item."""
    row = inner.locator(ACTION_CONTAINER).filter(
        has=inner.locator(ACTION_TITLE, has_text=button_text)
    ).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.locator(ACTION_MENU).first.click(timeout=UI_TIMEOUT)
    item = inner.locator(f'[data-qa="{_SUB_ACTION[intent]}"]').first
    item.wait_for(state="visible", timeout=UI_TIMEOUT)
    item.click(timeout=UI_TIMEOUT)


def edit_action(page: Page, button_text: str, new_button_text: str) -> None:
    """Rename an existing action's button text."""
    inner, outer = _enter_edit_mode(page)
    _open_action_menu(inner, button_text, "edit")
    title = outer.locator(BUTTON_TEXT_INPUT).first
    title.wait_for(state="visible", timeout=UI_TIMEOUT)
    title.fill(new_button_text, timeout=UI_TIMEOUT)
    _save_edit_dialog(page, inner)


def _toggle_action(page: Page, button_text: str, intent: str) -> None:
    inner, _ = _enter_edit_mode(page)
    _open_action_menu(inner, button_text, intent)
    done = inner.locator(DONE_BTN).first
    done.wait_for(state="visible", timeout=UI_TIMEOUT)
    done.click(timeout=UI_TIMEOUT)
    done.wait_for(state="detached", timeout=NAV_TIMEOUT)


def hide_action(page: Page, button_text: str) -> None:
    """Hide an action from the client portal (toggle visibility off)."""
    _toggle_action(page, button_text, "hide")


def show_action(page: Page, button_text: str) -> None:
    """Show a previously hidden action on the client portal (toggle visibility on)."""
    _toggle_action(page, button_text, "show")


def delete_action(page: Page, button_text: str) -> None:
    """Delete an action from the client portal editor."""
    _toggle_action(page, button_text, "delete")


def _read_cp_actions(page: Page, context: dict, portal_token: str) -> list[str] | None:
    """Open the client portal livesite as the client and read its action button labels.

    A fresh context is opened each call so the CP livesite is loaded uncached
    (mirrors the legacy reload), which is what lets editor changes become visible
    despite the CP action cache.

    Returns the action labels, or ``None`` if the livesite did not become ready in
    time (cold loads occasionally exceed CP_LOAD_TIMEOUT). ``None`` means "not ready,
    retry" so a single slow load does not fail the assertion — the polling caller
    re-opens a fresh context and tries again within its settle budget."""
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    try:
        cp_page = cp_context.new_page()
        cp_page.goto(
            f"{_vitrage_base(context)}/site/{pivot_uid(context)}/action?client_jwt={portal_token}",
            wait_until="domcontentloaded",
            timeout=NAV_TIMEOUT,
        )
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        cp_frame.locator(QUICK_ACTIONS).first.wait_for(state="visible", timeout=CP_LOAD_TIMEOUT)
        labels = cp_frame.locator(QUICK_ACTION).all_inner_texts()
        return [label.strip() for label in labels if label.strip()]
    except PlaywrightTimeoutError:
        return None
    finally:
        cp_context.close()


def assert_cp_displays(page: Page, context: dict, portal_token: str, action_text: str) -> None:
    """Assert the client portal livesite shows ``action_text`` (polls past CP cache lag)."""
    deadline = time.monotonic() + CP_SETTLE
    actions: list[str] | None = None
    while True:
        actions = _read_cp_actions(page, context, portal_token)
        if actions is not None and action_text in actions:
            return
        if time.monotonic() >= deadline:
            raise AssertionError(
                f"Client portal did not display action {action_text!r}; saw: {actions}"
            )
        page.wait_for_timeout(2_000)


def assert_cp_not_displays(page: Page, context: dict, portal_token: str, action_text: str) -> None:
    """Assert the client portal livesite no longer shows ``action_text`` (polls past cache lag)."""
    deadline = time.monotonic() + CP_SETTLE
    actions: list[str] | None = None
    while True:
        actions = _read_cp_actions(page, context, portal_token)
        if actions is not None and action_text not in actions:
            return
        if time.monotonic() >= deadline:
            raise AssertionError(
                f"Client portal still displays action {action_text!r}; saw: {actions}"
            )
        page.wait_for_timeout(2_000)
