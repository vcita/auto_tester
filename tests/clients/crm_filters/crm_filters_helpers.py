"""API setup + CRM UI helpers for the crm_filters migration (VCITA2-13790).

API setup (clients with tags/custom-field values, custom fields, products, open
payments) reuses the shared account plumbing in ``tests/account_api``. The CRM
UI helpers (filters, counter, views, columns, client-list reading) follow the
proven patterns in ``tests/clients/custom_status/status_helpers``.
"""

import re
import time
from typing import Iterable

import requests
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect

from tests.account_api import account_token, api_base

REQUEST_TIMEOUT = 20
UI_TIMEOUT = 5_000
CLIENTS_PAGE_TIMEOUT = 5_000
CLIENTS_READY_TIMEOUT = 5_000
FILTER_OPTION_TIMEOUT = 5_000
INDEX_TIMEOUT_SECONDS = 5
# A just-created custom-field definition takes a few seconds to propagate into
# the CRM column/filter metadata. This is backend data indexing (same class as
# the seeker indexing handled with poll-and-reload elsewhere), not a UI wait,
# so it is intentionally above the 5s UI cap.
FIELD_INDEX_TIMEOUT_SECONDS = 30
INDEX_RELOAD_ATTEMPTS = 3


# --------------------------------------------------------------------------- #
# API setup
# --------------------------------------------------------------------------- #
def _bearer(context: dict) -> dict:
    return {"Authorization": f"Bearer {account_token(context)}"}


def _post(context: dict, path: str, json: dict) -> dict:
    response = requests.post(
        f"{api_base(context)}{path}",
        json=json,
        headers=_bearer(context),
        timeout=REQUEST_TIMEOUT,
    )
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason} for {path}: {response.text[:500]}",
            response=response,
        )
    return response.json()


def create_client(context: dict, client: dict) -> dict:
    """Create a client. ``client`` may include ``tags`` and custom-field values
    (e.g. ``client_field``/``dropdown_field``) as top-level keys, mirroring the
    legacy ``/platform/v1/clients`` payload."""
    body = _post(context, "/platform/v1/clients", {**client, "source_name": "automation"})
    payload = body.get("data") or body
    created = payload.get("client") or payload
    client_id = created.get("id") or created.get("uid")
    if not client_id:
        raise ValueError(f"Client API response did not include an id: {body}")
    first = created.get("first_name") or client.get("first_name", "")
    last = created.get("last_name") or client.get("last_name", "")
    return {
        "id": client_id,
        "name": f"{first} {last}".strip(),
        "email": created.get("email") or client.get("email"),
    }


def create_field(context: dict, object_type: str, label: str, field_type: str,
                  possible_values: list | None = None) -> dict:
    """Create a custom field (matter/client). For dropdowns pass field_type
    ``dropdown`` with ``possible_values``."""
    field = {"object_type": object_type, "label": label, "type": field_type}
    if possible_values is not None:
        field["options"] = possible_values
    resp = requests.post(f"{api_base(context)}/platform/v1/fields", json=field,
                         headers=_bearer(context), timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return (resp.json().get("data") or resp.json())


def _settings_vue_frame(page: Page):
    """Inner Vuetage frame of the Client Card settings page (Angular -> Vue)."""
    outer = page.frame_locator('iframe[title="angularjs"]')
    return outer.frame_locator("#vue_iframe_layout")


def create_client_field_via_ui(page: Page, label: str, field_type_label: str,
                               options: list | None = None) -> None:
    """Create a client custom field through the Client Card Settings UI, mirroring
    legacy `ClientCardSettings.addCardField`. The platform `/fields` API rejects
    `object_type: client`, so client fields (incl. dropdowns) must be created here."""
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/settings/client_card", wait_until="domcontentloaded",
              timeout=CLIENTS_PAGE_TIMEOUT)
    inner = _settings_vue_frame(page)

    add_btn = inner.get_by_role("button", name=re.compile("Add client field", re.I)).first
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
        textarea = dialog.locator("textarea").first
        textarea.wait_for(state="visible", timeout=UI_TIMEOUT)
        textarea.fill("\n".join(options))

    dialog.get_by_role("button", name=re.compile(r"^Add$", re.I)).first.click()
    dialog.wait_for(state="hidden", timeout=UI_TIMEOUT)


def create_product(context: dict, name: str, price: float, currency: str = "USD") -> dict:
    body = _post(
        context,
        "/business/payments/v1/products",
        {"product": {"name": name, "price": price, "currency": currency, "display": True},
         "new_api": True},
    )
    return (body.get("data") or body).get("product") or (body.get("data") or body)


def assign_product(context: dict, client_id: str, product_id: str, price: float) -> dict:
    """Assign a product to a client (creates an open payment for that client)."""
    body = _post(
        context,
        "/business/payments/v1/product_orders",
        {"new_api": True, "product_order": {"client_id": client_id, "product_id": product_id,
                                            "price": price}},
    )
    return (body.get("data") or body).get("product_order") or (body.get("data") or body)


# --------------------------------------------------------------------------- #
# CRM navigation / readiness
# --------------------------------------------------------------------------- #
def open_clients_list(page: Page) -> None:
    if re.search(r"/app/clients/?$", page.url):
        wait_for_clients_table(page)
        return
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/clients", wait_until="domcontentloaded", timeout=CLIENTS_PAGE_TIMEOUT)
    page.wait_for_url("**/app/clients", timeout=CLIENTS_PAGE_TIMEOUT, wait_until="domcontentloaded")
    wait_for_clients_table(page)


def _active(page: Page):
    """The currently visible CRM view panel. Vuetify keeps every visited view's
    panel mounted in the DOM, so all view content (filter button, chips, counter,
    client rows) must be scoped to `.v-window-item--active` — a page-level lookup
    would match the hidden panels of other views."""
    return page.locator(".v-window-item--active").first


def wait_for_clients_table(page: Page) -> None:
    page.wait_for_url("**/app/clients**", timeout=CLIENTS_PAGE_TIMEOUT, wait_until="domcontentloaded")
    _active(page).locator(".table-actions__filter").first.wait_for(
        state="visible", timeout=CLIENTS_READY_TIMEOUT
    )
    # Wait for the CRM list skeleton to clear (the actual table loader, like the
    # legacy `pollPageForLoader(itemSkeleton)`). Best-effort + bounded.
    try:
        expect(_active(page).locator(".v-skeleton-loader__list-item")).to_have_count(
            0, timeout=CLIENTS_READY_TIMEOUT
        )
    except (PlaywrightTimeoutError, AssertionError):
        pass


# --------------------------------------------------------------------------- #
# Filters
# --------------------------------------------------------------------------- #
def _open_filters_menu(page: Page):
    wait_for_clients_table(page)
    filters_button = _active(page).locator(".table-actions__filter").first
    filters_button.wait_for(state="visible", timeout=CLIENTS_READY_TIMEOUT)
    filters_button.click()


def _apply_button(page):
    return page.locator('[data-qa="VcDropdown-content"] .VcButton').last


def _fill_filter_text(page: Page, value: str) -> None:
    field = page.locator('[data-qa="VcDropdown-content"] input').first
    field.wait_for(state="visible", timeout=FILTER_OPTION_TIMEOUT)
    field.click()
    field.fill("")
    field.press_sequentially(value, delay=20)


def add_text_filter(page: Page, option_qa: str, value: str) -> None:
    _open_filters_menu(page)
    option = page.locator(f'[data-qa="{option_qa}"]').first
    option.wait_for(state="visible", timeout=FILTER_OPTION_TIMEOUT)
    option.click()
    _fill_filter_text(page, value)
    apply_btn = _apply_button(page)
    apply_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    apply_btn.click()
    wait_for_clients_table(page)


def add_first_name_filter(page: Page, value: str) -> None:
    add_text_filter(page, "item-fields_filter.first_name", value)


def add_custom_field_filter(page: Page, field_name: str, value: str) -> None:
    add_text_filter(page, f"item-custom_fields_filter.{field_name}", value)


def add_tags_filter(page: Page, tag: str) -> None:
    _open_filters_menu(page)
    tags_option = page.locator('[data-qa="item-tags_filter"]').first
    tags_option.wait_for(state="visible", timeout=FILTER_OPTION_TIMEOUT)
    tags_option.click()
    option = page.locator(".vc-base-list-item, [role='option']").filter(has_text=tag).first
    option.wait_for(state="visible", timeout=FILTER_OPTION_TIMEOUT)
    option.click()
    apply_btn = _apply_button(page)
    apply_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    apply_btn.click()
    wait_for_clients_table(page)


def add_dropdown_field_filter(page: Page, field_name: str, option_value: str) -> None:
    _open_filters_menu(page)
    option = page.locator(f'[data-qa="item-custom_fields_filter.{field_name}"]').first
    option.wait_for(state="visible", timeout=FILTER_OPTION_TIMEOUT)
    option.click()
    item = page.locator(f'.vc-base-list-item[display_value="{option_value}"]').first
    item.wait_for(state="visible", timeout=FILTER_OPTION_TIMEOUT)
    # Vuetify hides the real <input>; click the rendered row/checkbox instead of check().
    item.click()
    apply_btn = _apply_button(page)
    apply_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    apply_btn.click()
    wait_for_clients_table(page)


def add_open_payments_filter(page: Page) -> None:
    _open_filters_menu(page)
    option = page.locator('[data-qa="item-matter_metadata_flat.payments.open"]').first
    option.wait_for(state="visible", timeout=FILTER_OPTION_TIMEOUT)
    option.click()
    wait_for_clients_table(page)


def edit_first_name_filter(page: Page, value: str) -> None:
    # Legacy edit re-applies the same filter type with the new value.
    add_first_name_filter(page, value)


def remove_filter(page: Page, filter_name: str) -> None:
    chip = _filter_chip_by_name(page, filter_name)
    chip.locator("button.v-chip__close").first.click()
    wait_for_clients_table(page)


def clear_all_filters(page: Page) -> None:
    clear_action = _active(page).get_by_text("Clear all", exact=True)
    if clear_action.count() == 0:
        return
    clear_action.first.click()
    expect(_active(page).get_by_text("Clear all", exact=True)).to_have_count(0, timeout=UI_TIMEOUT)
    wait_for_clients_table(page)


# --------------------------------------------------------------------------- #
# Filter / counter / client-list reads
# --------------------------------------------------------------------------- #
def _filter_chips(page: Page):
    return _active(page).locator(".active-filters .VcChip")


def _filter_chip_by_name(page: Page, filter_name: str):
    chips = _filter_chips(page)
    for index in range(chips.count()):
        chip = chips.nth(index)
        texts = chip.locator(".vc-tooltip__activator span span")
        if texts.count() > 0 and texts.first.inner_text().strip() == filter_name:
            return chip
    return _active(page).locator(f'[data-qa*="active-filter-chip-{filter_name}"]').first


def displayed_filter_names(page: Page) -> list[str]:
    container = _active(page).locator(".active-filters")
    if container.count() == 0 or not container.first.is_visible():
        return []
    names: list[str] = []
    chips = _filter_chips(page)
    for index in range(chips.count()):
        texts = chips.nth(index).locator(".vc-tooltip__activator span span")
        if texts.count() > 0:
            names.append(texts.first.inner_text().strip())
    return names


def assert_displayed_filters(page: Page, expected: Iterable[str]) -> None:
    expected_set = sorted(expected)
    deadline = time.monotonic() + INDEX_TIMEOUT_SECONDS
    actual: list[str] = []
    while time.monotonic() < deadline:
        actual = sorted(displayed_filter_names(page))
        if actual == expected_set:
            return
        time.sleep(0.3)
    raise AssertionError(f"Expected active filters {expected_set}, got {actual}")


def filtered_counter(page: Page) -> str:
    counter = _active(page).locator('[data-qa="summary-text"]').first
    counter.wait_for(state="visible", timeout=UI_TIMEOUT)
    return counter.inner_text().strip()


def assert_counter(page: Page, expected: str) -> None:
    deadline = time.monotonic() + INDEX_TIMEOUT_SECONDS
    actual = ""
    while time.monotonic() < deadline:
        actual = filtered_counter(page)
        if actual.upper() == expected.upper():
            return
        time.sleep(0.3)
    raise AssertionError(f"Expected counter {expected!r}, got {actual!r}")


def visible_client_names(page: Page) -> list[str]:
    view = _active(page)
    empty_state = view.locator('[data-qa="VcEmptyState"]')
    if empty_state.count() > 0 and empty_state.first.is_visible():
        return []
    names = view.locator('[data-qa="matter-name"]')
    return [names.nth(i).inner_text().strip() for i in range(names.count())]


def assert_filtered_clients(page: Page, expected_names: Iterable[str]) -> None:
    expected = sorted(expected_names)
    for attempt in range(INDEX_RELOAD_ATTEMPTS):
        deadline = time.monotonic() + INDEX_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            actual = sorted(visible_client_names(page))
            if actual == expected:
                return
            time.sleep(1)
        if attempt < INDEX_RELOAD_ATTEMPTS - 1:
            page.reload(wait_until="domcontentloaded", timeout=CLIENTS_PAGE_TIMEOUT)
            wait_for_clients_table(page)
    raise AssertionError(f"Expected filtered clients {expected}, got {sorted(visible_client_names(page))}")


# --------------------------------------------------------------------------- #
# Views
# --------------------------------------------------------------------------- #
def select_view(page: Page, view_name: str) -> None:
    """Select a preset view. Pinned views appear as tabs; others live behind the
    `crm-view-more-button` dropdown where each item carries a `name` attribute."""
    open_clients_list(page)
    tab = page.locator(
        f'[data-qa="VcTabs-tab-{view_name.replace(" ", "-")}"], [data-qa="VcTabs-tab-{view_name.replace(" ", "")}"]'
    ).first
    if tab.count() > 0 and tab.first.is_visible():
        tab.click()
        wait_for_clients_table(page)
        return
    more_button = page.locator('[data-qa="crm-view-more-button"]').first
    more_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    more_button.click()
    item = page.locator(f'[data-qa^="vc-list-"][name="{view_name}"]').first
    if item.count() == 0:
        item = page.locator(f'[name="{view_name}"]').first
    item.wait_for(state="visible", timeout=UI_TIMEOUT)
    item.click()
    wait_for_clients_table(page)


def select_tab(page: Page, tab_name: str) -> None:
    tab = page.locator(
        f'[data-qa="VcTabs-tab-{tab_name.replace(" ", "-")}"], [data-qa="VcTabs-tab-{tab_name.replace(" ", "")}"]'
    ).first
    tab.wait_for(state="visible", timeout=UI_TIMEOUT)
    tab.click()
    wait_for_clients_table(page)


def save_fixed_as_new_view(page: Page, view_name: str) -> None:
    save_button = _active(page).locator(".table-actions__save--margin").first
    save_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    save_button.click()
    modal = page.locator('[data-qa="crm-save-view-modal"]').first
    modal.wait_for(state="visible", timeout=UI_TIMEOUT)
    name_input = page.locator('[data-qa="crm-save-view-modal-input-view-name"]').first
    name_input.click()
    name_input.fill(view_name)
    page.locator('[data-qa="vc-footer-Save"]').first.click()
    wait_for_clients_table(page)


def save_custom_view(page: Page) -> None:
    save_button = _active(page).locator("button.table-actions__save").first
    save_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    save_button.click()
    # The split-button opens a menu with "Save" / "Save as new"; pick "Save".
    save_item = page.locator(".save-action-items__item").filter(has_text=re.compile(r"^Save$")).first
    if save_item.count() == 0:
        save_item = page.locator(".save-action-items__item").first
    save_item.wait_for(state="visible", timeout=UI_TIMEOUT)
    save_item.click()
    wait_for_clients_table(page)


# --------------------------------------------------------------------------- #
# Columns
# --------------------------------------------------------------------------- #
def _open_manage_columns(page: Page) -> Locator:
    """Multiple manage-columns lists can stay mounted (one per visited view), so
    scope to the visible items only."""
    _active(page).locator('[data-qa="CrmTable-All-manage-columns-button"]').first.click()
    items = page.locator('[data-qa="manage-columns-draggable-list-items--in-item"]:visible')
    items.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return items


def _close_manage_columns(page: Page) -> None:
    done = page.locator('[data-qa="vc-footer-Done"]:visible').first
    done.wait_for(state="visible", timeout=UI_TIMEOUT)
    done.click()
    wait_for_clients_table(page)


def add_column(page: Page, column: str) -> None:
    # A newly created custom field may not be in the column list yet; reopen the
    # dialog and, if still missing, reload the clients page and retry until the
    # field-index budget is exhausted.
    deadline = time.monotonic() + FIELD_INDEX_TIMEOUT_SECONDS
    while True:
        items = _open_manage_columns(page)
        target = items.filter(has_text=column).first
        if target.count() > 0:
            # Vuetify hides the real <input>, so a normal check() never becomes
            # actionable; toggle via the rendered checkbox like the legacy JS click.
            target.locator(".checkbox-label, label, .v-input--selection-controls__input").first.click()
            _close_manage_columns(page)
            return
        _close_manage_columns(page)
        if time.monotonic() >= deadline:
            raise AssertionError(f"Custom field column {column!r} never appeared in manage-columns list")
        page.reload(wait_until="domcontentloaded")
        wait_for_clients_table(page)


def table_columns(page: Page) -> list[str]:
    headers = _active(page).locator(".VcDataTable--header")
    return [headers.nth(i).inner_text().strip().upper() for i in range(headers.count())]


def assert_column_present(page: Page, column: str) -> None:
    expected = column.upper()
    deadline = time.monotonic() + INDEX_TIMEOUT_SECONDS
    cols: list[str] = []
    while time.monotonic() < deadline:
        cols = table_columns(page)
        if any(expected in c for c in cols):
            return
        time.sleep(0.3)
    raise AssertionError(f"Expected column {column!r} in CRM table, got {cols}")
