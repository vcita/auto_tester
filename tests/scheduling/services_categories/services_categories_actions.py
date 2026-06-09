"""Category + service mutation actions for the categories-and-services migration.

All actions run in the Angular frontage frame (``iframe[title="angularjs"]``) on the
Services index settings page. Angular-Material controls (menus, md-select, checkboxes)
use JS clicks where the standard click is intercepted by overlays, per the project's
Angular click guidance. Selectors mirror the legacy ``servicesSettings.js`` /
``serviceEditor.js`` page objects.
"""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from tests.scheduling.services_categories.services_categories_helpers import (
    CATEGORY_CARD,
    CATEGORY_TITLE,
    SERVICE_ROW,
    SERVICE_TITLE,
    SETTLE_MS,
    UI_TIMEOUT,
    goto_services,
)

OTHER_ADDRESS = "auto address1"


def _settle(page: Page) -> None:
    page.wait_for_timeout(SETTLE_MS)


def _set_other_address(page: Page, ng) -> None:
    """Select Face-to-face -> Other address and type a literal address.

    A fresh account has no saved business address, so the default "My business address"
    radio would fail validation; the legacy flow always sets an explicit other address.
    """
    ng.get_by_role("button", name=re.compile("Face to face")).click()
    other = ng.get_by_role("radio", name=re.compile("Other address"))
    other.wait_for(state="visible", timeout=UI_TIMEOUT)
    other.click()
    addr = ng.locator('[name="interaction_details"]')
    addr.wait_for(state="visible", timeout=UI_TIMEOUT)
    addr.fill(OTHER_ADDRESS)


def _open_new_service(page: Page, option_label: str):
    ng = goto_services(page)
    ng.get_by_role("button", name=re.compile("New service")).click()
    ng.get_by_role("menu").wait_for(state="visible", timeout=UI_TIMEOUT)
    ng.get_by_role("menuitem", name=re.compile(option_label)).click()
    ng.get_by_role("dialog").wait_for(state="visible", timeout=UI_TIMEOUT)
    return ng


def create_category(page: Page, name: str) -> None:
    ng = goto_services(page)
    ng.locator('[data-qa="newCategory"]').click()
    name_input = ng.locator('[name="category_name"]')
    name_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    name_input.fill(name)
    ng.get_by_role("button", name="Save").click()
    _settle(page)


def create_event_service(page: Page, name: str, price: str, max_attendees: int) -> None:
    """Create a require-to-pay group event (price + max attendees + require-to-pay)."""
    ng = _open_new_service(page, "Group event")
    ng.get_by_role("textbox", name="Service name *").fill(name)
    ng.get_by_role("spinbutton", name=re.compile("Max attendees")).fill(str(max_attendees))
    _set_other_address(page, ng)
    ng.get_by_role("button", name=re.compile("With fee")).click()
    price_field = ng.get_by_role("spinbutton", name="Service price *")
    price_field.wait_for(state="visible", timeout=UI_TIMEOUT)
    price_field.fill(price)
    require = ng.locator("md-checkbox[ng-model~='newService.require_to_pay']")
    require.wait_for(state="visible", timeout=UI_TIMEOUT)
    if require.get_attribute("aria-checked") != "true":
        require.evaluate("el => el.click()")
    ng.get_by_role("button", name="Create").click()
    _dismiss_event_times_dialog(ng)
    _settle(page)


def _dismiss_event_times_dialog(ng) -> None:
    later = ng.get_by_role("button", name="I'll do it later")
    try:
        later.wait_for(state="visible", timeout=3_000)
        later.click()
    except Exception:  # noqa: BLE001 - dialog only appears on first event
        pass


def create_appointment_service(page: Page, name: str, category: str) -> None:
    """Create a don't-display-fee 1-on-1 service inside ``category`` (advanced flow)."""
    ng = _open_new_service(page, "1 on 1 appointment")
    ng.get_by_role("textbox", name="Service name *").fill(name)
    _set_other_address(page, ng)
    ng.locator('button[data-qa="no-fee"]').click()
    ng.locator("md-dialog-actions button[ng-click='saveNewService(\"advanced\")']").click()
    _wait_editor(ng)
    _set_editor_category(page, ng, category)
    _save_editor(page, ng)


def edit_service_category(page: Page, service_name: str, category: str) -> None:
    ng = _open_service_editor(page, service_name)
    _set_editor_category(page, ng, category)
    _save_editor(page, ng)


def edit_service_name(page: Page, service_name: str, new_name: str) -> None:
    ng = _open_service_editor(page, service_name)
    name_field = ng.locator('input[name="name"]')
    name_field.wait_for(state="visible", timeout=UI_TIMEOUT)
    name_field.fill(new_name)
    _save_editor(page, ng)


def _open_service_editor(page: Page, service_name: str):
    ng = goto_services(page)
    row = ng.locator(SERVICE_ROW).filter(has=ng.locator(SERVICE_TITLE, has_text=service_name)).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.hover()
    edit_btn = row.get_by_role("button", name="icon-pencil-s")
    edit_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    edit_btn.click()
    page.wait_for_url("**/app/settings/services/**", timeout=UI_TIMEOUT)
    _wait_editor(ng)
    return ng


def _wait_editor(ng) -> None:
    ng.locator('input[name="name"]').wait_for(state="visible", timeout=UI_TIMEOUT)


def _set_editor_category(page: Page, ng, category: str) -> None:
    dropdown = ng.locator(".settings-input-container .md-text").first
    dropdown.wait_for(state="visible", timeout=UI_TIMEOUT)
    dropdown.evaluate("el => el.click()")
    option = ng.get_by_role("option", name=category, exact=True)
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.evaluate("el => el.click()")


def _save_editor(page: Page, ng) -> None:
    ng.get_by_role("button", name="Save").click()
    _settle(page)


def rename_category(page: Page, old_name: str, new_name: str) -> None:
    ng = goto_services(page)
    _open_category_menu(ng, old_name, "Rename")
    name_input = ng.locator('[name="category_name"]')
    name_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    name_input.fill(new_name)
    ng.get_by_role("button", name="Save").click()
    _settle(page)


def move_category_up(page: Page, name: str) -> None:
    """Move a category up one position and confirm the reorder before returning.

    A real click is used (not JS) so Angular's ng-click handler fires; the reorder is
    then confirmed by waiting until ``name`` is rendered as the first category card, so a
    subsequent re-navigation cannot race ahead of the (async) reorder persistence.
    """
    ng = goto_services(page)
    card = _category_card(ng, name)
    up = card.locator('.header-actions md-icon[aria-label="icon-arrow-up-s"]')
    up.wait_for(state="visible", timeout=UI_TIMEOUT)
    up.scroll_into_view_if_needed()
    up.click()
    first_title = ng.locator(CATEGORY_CARD).first.locator(CATEGORY_TITLE).first
    expect(first_title).to_contain_text(name, timeout=UI_TIMEOUT)


def delete_category(page: Page, name: str) -> None:
    """Delete a category and confirm it is gone before returning.

    deleteCategory triggers an async delete + forced reload; waiting until the category
    card disappears in-place (rather than a fixed settle) stops a subsequent
    re-navigation from racing ahead of the delete persistence.
    """
    ng = goto_services(page)
    _open_category_menu(ng, name, "Delete")
    _confirm_ok(ng)
    expect(ng.locator(CATEGORY_TITLE, has_text=name)).to_have_count(0, timeout=UI_TIMEOUT)


def delete_service(page: Page, service_name: str) -> None:
    """Delete a service via its editor Delete button (verified path), then confirm Ok."""
    ng = _open_service_editor(page, service_name)
    ng.get_by_role("button", name="Delete").click()
    _confirm_ok(ng)
    page.wait_for_url("**/app/settings/services", timeout=UI_TIMEOUT)
    _settle(page)


def clone_service(page: Page, service_name: str) -> None:
    """Clone a service via its row 3-dot menu (Clone -> Ok), then confirm the copy renders.

    The row `.actions` hold two controls: a direct edit (pencil) button and an `md-menu`
    whose icon button opens the Clone/Delete sub-menu. We hover the row to reveal them,
    open that menu button, pick "Clone", confirm, then wait for "Copy of <name>" to appear.
    """
    ng = goto_services(page)
    row = ng.locator(SERVICE_ROW).filter(has=ng.locator(SERVICE_TITLE, has_text=service_name)).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.hover()
    menu_btn = row.locator(".actions md-menu button").first
    menu_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    menu_btn.click()
    clone = ng.get_by_role("menuitem", name="Clone")
    clone.wait_for(state="visible", timeout=UI_TIMEOUT)
    clone.click()
    _confirm_ok(ng)
    copy = ng.locator(SERVICE_TITLE, has_text=f"Copy of {service_name}")
    copy.first.wait_for(state="visible", timeout=UI_TIMEOUT)


def _category_card(ng, name: str):
    return ng.locator(CATEGORY_CARD).filter(has=ng.locator(CATEGORY_TITLE, has_text=name)).first


def _open_category_menu(ng, name: str, option: str) -> None:
    card = _category_card(ng, name)
    card.wait_for(state="visible", timeout=UI_TIMEOUT)
    menu = card.locator('.header-actions md-icon[aria-label="icon-menu-s"]')
    menu.wait_for(state="visible", timeout=UI_TIMEOUT)
    menu.evaluate("el => el.click()")
    item = ng.get_by_role("menuitem", name=option)
    item.wait_for(state="visible", timeout=UI_TIMEOUT)
    item.click()


def _confirm_ok(ng) -> None:
    ok = ng.get_by_role("button", name="Ok")
    ok.wait_for(state="visible", timeout=UI_TIMEOUT)
    ok.click()
