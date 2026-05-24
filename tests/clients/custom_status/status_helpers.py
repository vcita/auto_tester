import re
import time
from typing import Iterable

import requests
from playwright.sync_api import Page, expect

REQUEST_TIMEOUT = 30
UI_TIMEOUT = 30000


def create_client_via_api(context: dict, client: dict) -> dict:
    response = _account_request(
        context,
        "POST",
        "/platform/v1/clients",
        json={**client, "source_name": "automation"},
    )
    payload = response.get("data") or response
    created_client = payload.get("client") or payload
    client_id = created_client.get("id") or created_client.get("uid")
    if not client_id:
        raise ValueError(f"Client API response did not include an id: {response}")

    first_name = created_client.get("first_name") or client["first_name"]
    last_name = created_client.get("last_name") or client["last_name"]
    return {
        "id": client_id,
        "name": f"{first_name} {last_name}".strip(),
        "email": created_client.get("email") or client["email"],
    }


def create_custom_status(page: Page, status_name: str) -> None:
    status_scope = open_client_status_settings(page)
    status_input = status_scope.get_by_placeholder("Add statuses")
    status_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    status_input.click()
    status_input.press_sequentially(status_name, delay=20)
    status_input.press("Enter")
    status_chip(status_scope, status_name).wait_for(state="visible", timeout=UI_TIMEOUT)


def assert_status_filter_options(page: Page, status_name: str, *, should_exist: bool) -> None:
    open_clients_list(page)
    open_status_filter(page)
    option = page.locator(".vc-base-list-item, [role='option']").filter(has_text=status_name)
    if should_exist:
        option.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    else:
        expect(option).to_have_count(0, timeout=10000)
    close_open_dropdown(page)


def apply_status_filter(page: Page, status_name: str) -> None:
    open_clients_list(page)
    open_status_filter(page)
    option = page.locator(".vc-base-list-item, [role='option']").filter(has_text=status_name).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()
    apply_button = page.locator('[data-qa="VcDropdown-content"] .VcButton').last
    apply_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    apply_button.click()
    wait_for_clients_table(page)


def clear_filters(page: Page) -> None:
    clear_action = page.get_by_text("Clear all", exact=True)
    if clear_action.count() == 0:
        return
    clear_action.first.click()
    expect(page.get_by_text("Clear all", exact=True)).to_have_count(0, timeout=UI_TIMEOUT)
    wait_for_clients_table(page)


def assert_filtered_clients(page: Page, expected_names: Iterable[str]) -> None:
    expected = sorted(expected_names)
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        actual = sorted(visible_client_names(page))
        if actual == expected:
            return
        time.sleep(1)
    raise AssertionError(f"Expected filtered clients {expected}, got {visible_client_names(page)}")


def open_client_from_list(page: Page, client_name: str, client_id: str | None = None) -> None:
    if client_id:
        app_base = page.url.split("/app/")[0]
        page.goto(f"{app_base}/app/clients/{client_id}", wait_until="domcontentloaded")
        page.wait_for_url("**/app/clients/**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
        return

    open_clients_list(page)
    clear_filters(page)
    search_field = page.get_by_role("searchbox").nth(1)
    search_field.wait_for(state="visible", timeout=UI_TIMEOUT)
    search_field.click()
    search_field.fill("")
    search_field.press_sequentially(client_name, delay=20)
    row = page.get_by_role("row").filter(has_text=client_name).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.click()
    page.wait_for_url("**/app/clients/**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")


def set_client_status(page: Page, status_name: str) -> None:
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator("#vue_iframe_layout")
    edit_button = inner.locator("div.contact-details button.edit-button")
    edit_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    edit_button.click()

    status_select = outer.locator('f-client-field[field="statusField"] md-select')
    status_select.wait_for(state="visible", timeout=UI_TIMEOUT)
    status_select.click()
    option = outer.get_by_role("option", name=status_name)
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()

    save_button = outer.get_by_role("button", name=re.compile(r"^Save$", re.I))
    save_button.click()
    assert_client_status(page, status_name)


def assert_client_status(page: Page, status_name: str) -> None:
    inner = page.frame_locator('iframe[title="angularjs"]').frame_locator("#vue_iframe_layout")
    status_value = inner.locator(".contact-status-value")
    expect(status_value).to_have_text(status_name, timeout=UI_TIMEOUT)


def attempt_delete_status_in_use(page: Page, status_name: str) -> None:
    status_scope = open_client_status_settings(page)
    click_status_delete(status_scope, status_name)
    dialog = visible_dialog(page)
    if dialog:
        dismiss = dialog.get_by_role("button", name=re.compile(r"Cancel|OK|Ok|Close", re.I)).first
        dismiss.click()
    status_chip(status_scope, status_name).wait_for(state="visible", timeout=UI_TIMEOUT)


def delete_unused_status(page: Page, status_name: str) -> None:
    status_scope = open_client_status_settings(page)
    click_status_delete(status_scope, status_name)
    confirm = page.get_by_role("button", name=re.compile(r"Delete|OK|Ok|Confirm", re.I)).last
    if confirm.count() > 0:
        confirm.click()
    expect(status_chip(status_scope, status_name)).to_have_count(0, timeout=UI_TIMEOUT)


def open_client_status_settings(page: Page):
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/settings/client_card", wait_until="domcontentloaded")
    outer = page.frame_locator('iframe[title="angularjs"]')
    status_scope = outer.frame_locator("#vue_iframe_layout")
    status_scope.get_by_role("tab", name=re.compile(r"Client status", re.I)).click()
    return status_scope


def status_chip(status_scope, status_name: str):
    return status_scope.locator("div.client-custom-statuses .v-chip").filter(has_text=status_name)


def click_status_delete(status_scope, status_name: str) -> None:
    chip = status_chip(status_scope, status_name)
    chip.wait_for(state="visible", timeout=UI_TIMEOUT)
    close_button = chip.locator(".v-chip__close, button, [aria-label='Close']").last
    close_button.click()


def visible_dialog(page: Page):
    candidates = [
        page.get_by_role("dialog"),
        page.frame_locator('iframe[title="angularjs"]').get_by_role("dialog"),
    ]
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        for candidate in candidates:
            if candidate.count() > 0 and candidate.first.is_visible():
                return candidate.first
        time.sleep(0.1)
    return None


def open_clients_list(page: Page) -> None:
    if re.search(r"/app/clients/?$", page.url):
        wait_for_clients_table(page)
        return
    app_base = page.url.split("/app/")[0]
    page.goto(f"{app_base}/app/clients", wait_until="domcontentloaded")
    page.wait_for_url("**/app/clients", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
    wait_for_clients_table(page)


def open_status_filter(page: Page) -> None:
    filters_button = page.locator(".table-actions__filter")
    filters_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    filters_button.click()
    status_filter = page.locator('[data-qa*="item-client_data_associated_with_field_filter"]').first
    status_filter.wait_for(state="visible", timeout=UI_TIMEOUT)
    status_filter.click()


def wait_for_clients_table(page: Page) -> None:
    page.locator(".table-actions__filter").first.wait_for(state="visible", timeout=UI_TIMEOUT)


def visible_client_names(page: Page) -> list[str]:
    empty_state = page.locator('[data-qa="VcEmptyState"]')
    if empty_state.count() > 0 and empty_state.first.is_visible():
        return []
    names = page.locator('[data-qa="matter-name"]')
    return [names.nth(index).inner_text().strip() for index in range(names.count())]


def close_open_dropdown(page: Page) -> None:
    page.keyboard.press("Escape")


def _account_request(context: dict, method: str, path: str, **kwargs) -> dict:
    response = requests.request(
        method,
        f"{_resolve_api_base_url(context)}{path}",
        headers=_account_headers(context),
        timeout=REQUEST_TIMEOUT,
        **kwargs,
    )
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason} for {path}: {response.text[:500]}",
            response=response,
        )
    return response.json()


def _resolve_api_base_url(context: dict) -> str:
    api_base_url = context.get("api_base_url")
    if api_base_url:
        return api_base_url.rstrip("/")
    base_url = (context.get("base_url") or "").rstrip("/")
    if "meet2know.com" in base_url:
        return "https://api2.meet2know.com"
    if "vcita.com" in base_url:
        return "https://api.vcita.biz"
    if "app-" in base_url and ".external.int-eks.vchost.co" in base_url:
        return base_url.replace("https://app-", "https://core-", 1)
    raise ValueError("api_base_url is missing from context and could not be inferred")


def _account_headers(context: dict) -> dict:
    auto_account = context.get("auto_account") or {}
    token = auto_account.get("api_token") or auto_account.get("auth_token")
    if not token:
        raise ValueError("auto_account api_token is missing from context")
    return {"Authorization": f"Bearer {token}"}
