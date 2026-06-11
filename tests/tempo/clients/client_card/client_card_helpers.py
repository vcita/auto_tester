"""Client Card Settings helpers for the client_card migration (VCITA2-13855).

Covers the legacy `client-card.feature` flow: add a client/contact custom field
through the Client Card Settings UI, then rename it. CRM list seeding and
filtering reuse the proven helpers in ``tests/clients/crm_filters`` so the
custom-field filter + filtered-client assertions stay identical to the migrated
CRM coverage.
"""

import re
import time

from playwright.sync_api import Page

from tests.tempo.clients.crm_filters.crm_filters_helpers import (  # noqa: F401  (re-exported for the test)
    CLIENTS_PAGE_TIMEOUT,
    FILTER_OPTION_TIMEOUT,
    UI_TIMEOUT,
    _apply_button,
    _fill_filter_text,
    _open_filters_menu,
    _settings_vue_frame,
    assert_filtered_clients,
    clear_all_filters,
    create_client,
    open_clients_list,
    wait_for_clients_table,
)

SETTINGS_PATH = "/app/settings/client_card"
# A freshly created custom field takes a few seconds to surface in the CRM filter
# metadata (backend indexing, same class as the crm_filters field-index wait).
FIELD_INDEX_TIMEOUT_SECONDS = 30


def _goto_settings(page: Page):
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}{SETTINGS_PATH}", wait_until="domcontentloaded",
              timeout=CLIENTS_PAGE_TIMEOUT)
    return _settings_vue_frame(page)


def add_card_field(page: Page, card_type: str, label: str, field_type_label: str,
                   options: list | None = None) -> None:
    """Add a client/contact custom field via Client Card Settings (legacy
    `ClientCardSettings.addCardField`). ``card_type`` is 'client' or 'contact'."""
    inner = _goto_settings(page)

    button_label = "Add client field" if card_type == "client" else "Add contact field"
    add_btn = inner.get_by_role("button", name=re.compile(button_label, re.I)).first
    add_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    add_btn.click()

    dialog = inner.locator(".client-card-field-dialog").first
    dialog.wait_for(state="visible", timeout=UI_TIMEOUT)

    dialog.locator(".v-select__slot").first.click()
    option = inner.locator(".v-list-item, [role='option']").filter(
        has_text=re.compile(re.escape(field_type_label), re.I)).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()

    name_input = dialog.locator(".v-text-field__slot input").first
    name_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    name_input.fill(label)

    if options:
        dialog.locator("textarea").first.fill("\n".join(options))

    dialog.get_by_role("button", name=re.compile(r"^Add$", re.I)).first.click()
    dialog.wait_for(state="hidden", timeout=UI_TIMEOUT)


def edit_card_field(page: Page, origin_name: str, updated_name: str) -> None:
    """Rename an existing client/contact field (legacy
    `ClientCardSettings.editCardField`) and confirm the new name renders."""
    inner = _goto_settings(page)
    items = inner.locator(".client-field-list-item")
    items.first.wait_for(state="visible", timeout=UI_TIMEOUT)

    target = None
    for index in range(items.count()):
        item = items.nth(index)
        name = item.locator(".field-name").first
        if name.count() > 0 and name.inner_text().strip() == origin_name:
            target = item
            break
    if target is None:
        raise AssertionError(f"Card field {origin_name!r} not found in the settings list")
    target.click()

    dialog = inner.locator(".client-card-field-dialog").first
    dialog.wait_for(state="visible", timeout=UI_TIMEOUT)
    name_input = dialog.locator(".v-text-field__slot input").first
    name_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    name_input.fill(updated_name)
    dialog.get_by_role("button", name=re.compile(r"^Save$", re.I)).first.click()

    # Confirm the rename persisted: the renamed field renders in the settings list
    # (save is a backend write, so allow a little longer than the plain UI cap).
    inner.get_by_text(updated_name, exact=True).first.wait_for(
        state="visible", timeout=CLIENTS_PAGE_TIMEOUT + UI_TIMEOUT
    )


def add_field_filter(page: Page, field_name: str, value: str) -> None:
    """Filter the CRM list by a client/contact custom field's text value.

    Client (matter) and contact custom fields surface under slightly different
    filter data-qa namespaces, so match any option ending in
    ``custom_fields_filter.<field_name>``. A just-created field can lag the filter
    metadata, so reopen the menu until the option appears."""
    clear_all_filters(page)
    deadline = time.monotonic() + FIELD_INDEX_TIMEOUT_SECONDS
    selector = f'[data-qa$="custom_fields_filter.{field_name}"]'
    while True:
        _open_filters_menu(page)
        option = page.locator(selector).first
        if option.count() == 0:
            # Contact custom fields sit under a collapsed "Contact info" section;
            # expand it (legacy `item-show-more-contact_info`) and re-check.
            show_more = page.locator('[data-qa="item-show-more-contact_info"]').first
            if show_more.count() > 0:
                show_more.click()
                option = page.locator(selector).first
        if option.count() > 0:
            option.wait_for(state="visible", timeout=FILTER_OPTION_TIMEOUT)
            option.click()
            _fill_filter_text(page, value)
            apply_btn = _apply_button(page)
            apply_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
            apply_btn.click()
            wait_for_clients_table(page)
            return
        page.keyboard.press("Escape")
        if time.monotonic() >= deadline:
            raise AssertionError(f"Custom-field filter for {field_name!r} never appeared")
        page.reload(wait_until="domcontentloaded")
        wait_for_clients_table(page)
