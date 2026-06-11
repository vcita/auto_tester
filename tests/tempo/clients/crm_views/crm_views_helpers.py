"""API setup + CRM-views UI helpers for the crm_views migration (VCITA2-13951).

Ports the legacy `pages/desktop/Frontage/Clients/newClients.js` view actions
(create/edit/delete view, three-dot menu reads, close tab, select view, view
availability) to Playwright, using the same stable ``data-qa`` selectors.

API setup (staff create) and the SSO staff-switch reuse the shared, proven
helpers: ``account_api.create_platform_staff_via_api`` and the
``calendar_api`` partner-SSO primitives (the same ones the multistaff/calendar
migrations switch staff with on integration).
"""

from __future__ import annotations

from urllib.parse import quote

from playwright.sync_api import (
    Error as PlaywrightError,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)

from tests.account_api import account_request, create_platform_staff_via_api, pivot_uid
from tests.tempo.scheduling.calendar.calendar_api import (
    get_sso_token,
    resolve_partner_base_url,
    staff_uid,
)

UI_TIMEOUT = 5_000
CLIENTS_PAGE_TIMEOUT = 5_000

# Legacy permission/edit menu strings (clients.js getThreeDotMenuTexts contract).
PERMISSION_ACCOUNT_TEXT = "View is visible to all staff"
PERMISSION_STAFF_TEXT = "View is visible only to you"
NOT_EDITABLE_TEXT = "View can't be edited or deleted"


# --------------------------------------------------------------------------- #
# data-qa selector builders (mirror legacy newClients.js, space -> "-" or "")
# --------------------------------------------------------------------------- #
def _dq_variants(prefix: str, name: str, suffix: str = "") -> str:
    dashed = name.replace(" ", "-")
    squashed = name.replace(" ", "")
    return (
        f'[data-qa="{prefix}{dashed}{suffix}"], '
        f'[data-qa="{prefix}{squashed}{suffix}"]'
    )


def _tab(page: Page, name: str):
    return page.locator(_dq_variants("VcTabs-tab-", name)).first


def _close_button(page: Page, name: str):
    return page.locator(_dq_variants("VcTabs-close-", name)).first


def _three_dots(page: Page, name: str):
    return page.locator(_dq_variants("VcTabs-VcDropdown-more-tab-", name, "-three-dots")).first


def _menu_header(page: Page, name: str):
    return page.locator(_dq_variants("VcTabs-VcDropdown-more-tab-", name, "-header")).first


def _edit_action(page: Page, name: str):
    return page.locator(_dq_variants("VcTabs-tab-", name, "-actionItem-0")).first


def _delete_action(page: Page, name: str):
    return page.locator(_dq_variants("VcTabs-tab-", name, "-actionItem-1")).first


# --------------------------------------------------------------------------- #
# API setup + SSO staff switching
# --------------------------------------------------------------------------- #
def capture_owner(context: dict) -> dict:
    """Return the account owner staff {uid, display_name}. Call BEFORE creating
    extra staff so the owner is unambiguously the first staff."""
    response = account_request(
        context, "GET", f"/platform/v1/businesses/{pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for the owner lookup")
    owner = staffs[0]
    uid = owner.get("id") or owner.get("uid")
    context["account_first_staff_uid"] = uid
    return {"uid": uid, "display_name": owner.get("display_name") or owner.get("full_name")}


def create_staff_user(context: dict, name: str, email: str, role: str = "user") -> dict:
    """Create a Platform staff member (POST + GET read-back inside the shared helper)."""
    return create_platform_staff_via_api(context, name, email, role)


def _end_sessions(context: dict, uid: str) -> None:
    account_request(
        context,
        "DELETE",
        f"/platform/v1/businesses/{pivot_uid(context)}/staffs/{uid}/sessions",
    )


def _sso_login(page: Page, context: dict, staff: dict) -> None:
    token = get_sso_token(context, staff)
    base_url = resolve_partner_base_url(context)
    redirect_to = quote("/app/dashboard", safe="")
    try:
        page.goto(
            f"{base_url}/v1/partners/sso/login?staff_uid={staff_uid(staff)}"
            f"&sso_token={token}&redirect_to={redirect_to}",
            wait_until="domcontentloaded",
            timeout=UI_TIMEOUT,
        )
    except PlaywrightError as error:
        if "ERR_ABORTED" not in str(error):
            raise
    page.wait_for_url("**/app/dashboard**", timeout=UI_TIMEOUT)


def switch_to_staff(page: Page, context: dict, owner: dict, staff: dict) -> None:
    """Switch the logged-in session to ``staff`` (mirrors legacy "switching logged
    in staff to X via API": end the owner's sessions, then SSO-login as the staff).

    The target staff's own sessions are also ended first: across repeated
    owner<->staff switches a stale server-side staff session makes the partner
    SSO login bounce to the directory login ("signed out") instead of
    establishing a fresh staff session.
    """
    _end_sessions(context, owner["uid"])
    _end_sessions(context, staff["uid"])
    _sso_login(page, context, staff)


def login_as_admin(page: Page, context: dict, owner: dict) -> None:
    """Re-login as the account owner via SSO (legacy "user logged in to automatic
    account via API")."""
    _sso_login(page, context, owner)


# --------------------------------------------------------------------------- #
# CRM navigation / readiness
# --------------------------------------------------------------------------- #
def _active(page: Page):
    return page.locator(".v-window-item--active").first


def open_clients_list(page: Page) -> None:
    if page.url.rstrip("/").endswith("/app/clients"):
        wait_for_clients_table(page)
        return
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/clients", wait_until="domcontentloaded", timeout=CLIENTS_PAGE_TIMEOUT)
    wait_for_clients_table(page)


def wait_for_clients_table(page: Page) -> None:
    page.wait_for_url("**/app/clients**", timeout=CLIENTS_PAGE_TIMEOUT, wait_until="domcontentloaded")
    _active(page).locator(".table-actions__filter").first.wait_for(
        state="visible", timeout=UI_TIMEOUT
    )
    try:
        expect(_active(page).locator(".v-skeleton-loader__list-item")).to_have_count(
            0, timeout=UI_TIMEOUT
        )
    except (PlaywrightTimeoutError, AssertionError):
        pass


# --------------------------------------------------------------------------- #
# Tabs
# --------------------------------------------------------------------------- #
def close_tab(page: Page, name: str) -> None:
    """Close a pinned tab (legacy closeTab): click the tab, click its close icon,
    then confirm it is no longer pinned."""
    open_clients_list(page)
    tab = _tab(page, name)
    tab.wait_for(state="visible", timeout=UI_TIMEOUT)
    tab.click()
    wait_for_clients_table(page)
    close_btn = _close_button(page, name)
    close_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    close_btn.click()
    expect(_tab(page, name)).to_have_count(0, timeout=UI_TIMEOUT)


# --------------------------------------------------------------------------- #
# Create / edit / delete views
# --------------------------------------------------------------------------- #
def _fill_view_form(page: Page, name: str, description: str, level: str) -> None:
    modal = page.locator('[data-qa="crm-save-view-modal"]:visible').first
    modal.wait_for(state="visible", timeout=UI_TIMEOUT)
    name_input = modal.locator('[data-qa="crm-save-view-modal-input-view-name"]').first
    name_input.click()
    name_input.fill(name)
    desc_input = modal.locator('[data-qa="crm-save-view-modal-input-view-description"]').first
    desc_input.click()
    desc_input.fill(description)
    level_qa = (
        "crm-save-view-modal-segment-level-item-account"
        if level == "account"
        else "crm-save-view-modal-segment-level-item-staff"
    )
    modal.locator(f'[data-qa="{level_qa}"]').first.click()
    modal.locator('[data-qa="vc-footer-Save"]').first.click()
    modal.wait_for(state="hidden", timeout=UI_TIMEOUT)


def create_view(page: Page, name: str, description: str, level: str) -> None:
    """Create a CRM view via the New button (legacy createView)."""
    open_clients_list(page)
    page.locator('[data-qa="new-button"]').first.click()
    page.locator('[data-qa="more-actions-button_add_custom_view"]').first.click()
    _fill_view_form(page, name, description, level)
    _tab(page, name).wait_for(state="visible", timeout=UI_TIMEOUT)
    wait_for_clients_table(page)


def edit_view(page: Page, view_name: str, new_name: str, description: str, level: str) -> None:
    """Edit an existing view through its three-dot menu (legacy editView)."""
    _open_three_dot_menu(page, view_name)
    edit_action = _edit_action(page, view_name)
    edit_action.wait_for(state="visible", timeout=UI_TIMEOUT)
    edit_action.click()
    _fill_view_form(page, new_name, description, level)
    _tab(page, new_name).wait_for(state="visible", timeout=UI_TIMEOUT)
    wait_for_clients_table(page)


def delete_view(page: Page, view_name: str) -> None:
    """Delete a view through its three-dot menu (legacy deleteView)."""
    _open_three_dot_menu(page, view_name)
    delete_action = _delete_action(page, view_name)
    delete_action.wait_for(state="visible", timeout=UI_TIMEOUT)
    delete_action.click()
    confirm = page.locator('[data-qa="vc-footer-Delete"]').first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click()
    expect(_tab(page, view_name)).to_have_count(0, timeout=UI_TIMEOUT)
    wait_for_clients_table(page)


# --------------------------------------------------------------------------- #
# View selection / availability / three-dot menu reads
# --------------------------------------------------------------------------- #
def _more_button(page: Page):
    return page.locator('[data-qa="crm-view-more-button"]').first


def select_view(page: Page, view_name: str) -> None:
    """Select a view (legacy selectViewFromList): click the pinned tab if present,
    otherwise pick it from the views overflow dropdown (item carries name=...)."""
    open_clients_list(page)
    tab = _tab(page, view_name)
    if tab.count() > 0 and tab.first.is_visible():
        tab.click()
        wait_for_clients_table(page)
        return
    more = _more_button(page)
    more.wait_for(state="visible", timeout=UI_TIMEOUT)
    more.click()
    item = page.locator(f'[name="{view_name}"]').first
    item.wait_for(state="visible", timeout=UI_TIMEOUT)
    item.click()
    _tab(page, view_name).wait_for(state="visible", timeout=UI_TIMEOUT)
    wait_for_clients_table(page)


def _unpinned_view_names(page: Page) -> list[str]:
    """Names listed in the views overflow dropdown (legacy getUnpinnedViews)."""
    more = _more_button(page)
    if more.count() == 0 or not more.first.is_visible():
        return []
    more.click()
    items = page.locator('[data-qa="vc-list"] [name], [data-qa="vc-list"] .vc-base-list-item')
    names: list[str] = []
    for index in range(items.count()):
        item = items.nth(index)
        name = item.get_attribute("name") or item.inner_text()
        if name:
            names.append(name.strip())
    page.keyboard.press("Escape")
    return names


def assert_view_not_available(page: Page, view_name: str) -> None:
    """Assert the view is neither a pinned tab nor in the overflow dropdown
    (legacy "view X is not available": tabIsNotPinned + getUnpinnedViews)."""
    open_clients_list(page)
    expect(_tab(page, view_name)).to_have_count(0, timeout=UI_TIMEOUT)
    unpinned = _unpinned_view_names(page)
    assert view_name not in unpinned, (
        f"View {view_name!r} should not be available to this staff, "
        f"but appears in the views dropdown: {unpinned}"
    )


def _open_three_dot_menu(page: Page, view_name: str):
    """Open a view's three-dot menu (legacy openThreeDotMenu): select the view so it
    is the active tab, hover it to reveal the three-dots, then open the menu."""
    select_view(page, view_name)
    tab = _tab(page, view_name)
    tab.wait_for(state="visible", timeout=UI_TIMEOUT)
    tab.click()
    tab.hover()
    dots = _three_dots(page, view_name)
    dots.wait_for(state="visible", timeout=UI_TIMEOUT)
    dots.click()
    header = _menu_header(page, view_name)
    header.wait_for(state="visible", timeout=UI_TIMEOUT)
    return header


def view_menu_texts(page: Page, view_name: str) -> list[str]:
    """Return the three-dot menu lines (legacy getThreeDotMenuTexts)."""
    header = _open_three_dot_menu(page, view_name)
    text = header.inner_text()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    page.keyboard.press("Escape")
    return lines


def assert_view_description(page: Page, view_name: str, expected: str) -> None:
    lines = view_menu_texts(page, view_name)
    assert lines and lines[0] == expected, (
        f"Expected description {expected!r} in {view_name!r} menu, got {lines}"
    )


def assert_view_permission(page: Page, view_name: str, level: str) -> None:
    expected = PERMISSION_ACCOUNT_TEXT if level == "account" else PERMISSION_STAFF_TEXT
    lines = view_menu_texts(page, view_name)
    assert expected in lines, (
        f"Expected permission {expected!r} ({level}) in {view_name!r} menu, got {lines}"
    )


def assert_view_not_editable(page: Page, view_name: str) -> None:
    """Assert edit/delete are not available in the view menu (legacy "in X view menu
    edit and delete actions are not available")."""
    lines = view_menu_texts(page, view_name)
    assert NOT_EDITABLE_TEXT in lines, (
        f"Expected {NOT_EDITABLE_TEXT!r} in {view_name!r} menu, got {lines}"
    )
