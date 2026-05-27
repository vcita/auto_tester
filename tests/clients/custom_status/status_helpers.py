import re
import time
from typing import Iterable

import requests
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

REQUEST_TIMEOUT = 5
UI_TIMEOUT = 5000
CLIENTS_PAGE_TIMEOUT = 5_000
CLIENTS_READY_TIMEOUT = 5_000
SETTINGS_READY_TIMEOUT = 5_000
SETTINGS_READY_ATTEMPTS = 3
FILTER_OPTION_TIMEOUT = 5_000
CLIENT_INDEX_TIMEOUT_SECONDS = 5


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


def apply_status_filter(page: Page, status_name: str) -> None:
    last_error: PlaywrightTimeoutError | None = None
    for attempt in range(3):
        open_clients_list(page)
        open_status_filter(page)
        option = page.locator(".vc-base-list-item, [role='option']").filter(has_text=status_name).first
        option.wait_for(state="visible", timeout=FILTER_OPTION_TIMEOUT)
        option.click()
        apply_button = page.locator('[data-qa="VcDropdown-content"] .VcButton').last
        apply_button.wait_for(state="visible", timeout=UI_TIMEOUT)
        apply_button.click()
        try:
            wait_for_clients_table(page)
            return
        except PlaywrightTimeoutError as exc:
            last_error = exc
            if attempt == 2:
                raise

    raise last_error or AssertionError("Status filter did not load clients table")


def clear_filters(page: Page) -> None:
    clear_action = page.get_by_text("Clear all", exact=True)
    if clear_action.count() == 0:
        return
    clear_action.first.click()
    expect(page.get_by_text("Clear all", exact=True)).to_have_count(0, timeout=UI_TIMEOUT)
    wait_for_clients_table(page)


def assert_filtered_clients(page: Page, expected_names: Iterable[str]) -> None:
    expected = sorted(expected_names)
    for attempt in range(2):
        deadline = time.monotonic() + CLIENT_INDEX_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            actual = sorted(visible_client_names(page))
            if actual == expected:
                return
            time.sleep(1)
        if attempt == 0:
            page.reload(wait_until="domcontentloaded", timeout=CLIENTS_PAGE_TIMEOUT)
            wait_for_clients_table(page)
    raise AssertionError(f"Expected filtered clients {expected}, got {visible_client_names(page)}")


def open_client_from_list(page: Page, client_name: str, client_id: str | None = None) -> None:
    if client_id:
        app_base = page.url.split("/app/")[0]
        page.goto(
            f"{app_base}/app/clients/{client_id}",
            wait_until="domcontentloaded",
            timeout=CLIENTS_PAGE_TIMEOUT,
        )
        page.wait_for_url("**/app/clients/**", timeout=CLIENTS_PAGE_TIMEOUT, wait_until="domcontentloaded")
        wait_for_client_detail(page, client_name)
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
    page.wait_for_url("**/app/clients/**", timeout=CLIENTS_PAGE_TIMEOUT, wait_until="domcontentloaded")
    wait_for_client_detail(page, client_name)


def set_client_status(page: Page, status_name: str) -> None:
    page.locator('iframe[title="angularjs"]').wait_for(state="visible", timeout=UI_TIMEOUT)
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator("#vue_iframe_layout")
    print("    Opening edit contact dialog...")
    open_contact_edit_dialog(page, outer, inner)

    print("    Selecting client status...")
    status_select = first_visible_locator(
        [
            outer.locator('f-client-field[field="statusField"] md-select'),
            outer.locator('md-select[aria-label="Status"]'),
            outer.locator("md-select").filter(has_text=re.compile(r"Lead|Customer", re.I)),
            outer.locator("md-select"),
            page.locator('f-client-field[field="statusField"] md-select'),
            page.locator('md-select[aria-label="Status"]'),
            page.locator("md-select").filter(has_text=re.compile(r"Lead|Customer", re.I)),
        ]
    )
    status_select.wait_for(state="visible", timeout=UI_TIMEOUT)
    status_select.click()
    option = first_visible_locator(
        [
            outer.get_by_role("option", name=status_name),
            outer.locator("md-option").filter(has_text=status_name),
            page.get_by_role("option", name=status_name),
            page.locator("md-option").filter(has_text=status_name),
        ]
    )
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()

    print("    Saving client status...")
    save_button = first_visible_locator(
        [
            outer.get_by_role("button", name=re.compile(r"^Save$", re.I)),
            page.get_by_role("button", name=re.compile(r"^Save$", re.I)),
        ]
    )
    save_button.click()
    print("    Verifying client status...")
    assert_client_status(page, status_name)


def open_contact_edit_dialog(page: Page, outer, inner) -> None:
    dialog_titles = [outer.locator("text=Edit contact info"), page.locator("text=Edit contact info")]
    send_edit_contact_message(page)
    if wait_for_any_visible(dialog_titles, timeout=1_000):
        return

    candidates = [
        page.locator(".contact-header .edit-button"),
        page.locator(".contact-extra .edit-button"),
        inner.locator(".contact-header .edit-button"),
        inner.locator(".contact-extra .edit-button"),
        inner.locator("div.contact-details .edit-button"),
    ]
    last_error: PlaywrightTimeoutError | None = None
    for candidate in candidates:
        try:
            candidate.first.wait_for(state="visible", timeout=UI_TIMEOUT)
        except PlaywrightTimeoutError as exc:
            last_error = exc
            continue
        click_first_visible(candidate, force=True)
        if wait_for_any_visible(dialog_titles, timeout=1_000):
            return
    raise last_error or AssertionError("Edit contact info dialog did not open")


def send_edit_contact_message(page: Page) -> None:
    for frame in page.frames[1:]:
        try:
            frame.evaluate(
                """
                () => window.parent.postMessage({
                    event: 'vue-message',
                    origin: 'vue_iframe_layout',
                    data: {
                        eventName: 'matter_action',
                        data: { action: 'edit_contact' }
                    }
                }, '*')
                """
            )
        except Exception:
            continue


def assert_client_status(page: Page, status_name: str) -> None:
    inner = page.frame_locator('iframe[title="angularjs"]').frame_locator("#vue_iframe_layout")
    status_value = inner.locator(".contact-status-value")
    expect(status_value).to_have_text(status_name, timeout=UI_TIMEOUT)


def attempt_delete_status_in_use(page: Page, status_name: str) -> None:
    status_scope = open_client_status_settings(page)
    click_status_delete(status_scope, status_name)
    dismiss_status_delete_blocker_if_visible(page)
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
    last_error: PlaywrightTimeoutError | None = None

    for attempt in range(SETTINGS_READY_ATTEMPTS):
        page.goto(
            f"{app_base}/app/settings/client_card",
            wait_until="domcontentloaded",
            timeout=SETTINGS_READY_TIMEOUT,
        )
        try:
            page.wait_for_url(
                "**/app/settings/client_card**",
                timeout=SETTINGS_READY_TIMEOUT,
                wait_until="domcontentloaded",
            )
            page.locator('iframe[title="angularjs"]').wait_for(
                state="visible",
                timeout=SETTINGS_READY_TIMEOUT,
            )
            outer = page.frame_locator('iframe[title="angularjs"]')
            status_scope = outer.frame_locator("#vue_iframe_layout")
            tab = status_scope.get_by_role("tab", name=re.compile(r"Client status", re.I))
            tab.wait_for(state="visible", timeout=SETTINGS_READY_TIMEOUT)
            tab.click()
            status_scope.get_by_placeholder("Add statuses").wait_for(
                state="visible",
                timeout=SETTINGS_READY_TIMEOUT,
            )
            return status_scope
        except PlaywrightTimeoutError as exc:
            last_error = exc
            if attempt == SETTINGS_READY_ATTEMPTS - 1:
                raise

    raise last_error or AssertionError("Client status settings did not become ready")


def status_chip(status_scope, status_name: str):
    return status_scope.locator("div.client-custom-statuses .v-chip").filter(has_text=status_name)


def click_status_delete(status_scope, status_name: str) -> None:
    chip = status_chip(status_scope, status_name)
    chip.wait_for(state="visible", timeout=UI_TIMEOUT)
    close_button = chip.locator(".v-chip__close, button, [aria-label='Close']").last
    close_button.click()


def dismiss_status_delete_blocker_if_visible(page: Page) -> None:
    candidates = [
        (
            page.get_by_text("Cannot delete status", exact=True),
            page.get_by_text("Ok", exact=True),
        ),
        (
            page.frame_locator('iframe[title="angularjs"]').get_by_text(
                "Cannot delete status", exact=True
            ),
            page.frame_locator('iframe[title="angularjs"]').get_by_text("Ok", exact=True),
        ),
        (
            page.frame_locator('iframe[title="angularjs"]')
            .frame_locator("#vue_iframe_layout")
            .get_by_text("Cannot delete status", exact=True),
            page.frame_locator('iframe[title="angularjs"]')
            .frame_locator("#vue_iframe_layout")
            .get_by_text("Ok", exact=True),
        ),
    ]
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        for title, ok_button in candidates:
            if title.count() > 0 and title.first.is_visible():
                click_first_visible(ok_button)
                title.first.wait_for(state="hidden", timeout=UI_TIMEOUT)
                return
        time.sleep(0.1)


def click_first_visible(locator, force: bool = False) -> None:
    for index in range(locator.count()):
        candidate = locator.nth(index)
        if candidate.is_visible():
            candidate.click(force=force)
            return
    locator.first.click(force=force)


def first_visible_locator(locators):
    deadline = time.monotonic() + (UI_TIMEOUT / 1000)
    for locator in locators:
        try:
            if locator.count() > 0 and locator.first.is_visible():
                return locator.first
        except Exception:
            pass
    while time.monotonic() < deadline:
        for locator in locators:
            try:
                if locator.count() > 0 and locator.first.is_visible():
                    return locator.first
            except Exception:
                continue
        time.sleep(0.1)
    raise PlaywrightTimeoutError("No visible locator found")


def wait_for_any_visible(locators, timeout: int) -> bool:
    deadline = time.monotonic() + (timeout / 1000)
    while time.monotonic() < deadline:
        for locator in locators:
            try:
                if locator.count() > 0 and locator.first.is_visible():
                    return True
            except Exception:
                continue
        time.sleep(0.1)
    return False


def open_clients_list(page: Page) -> None:
    if re.search(r"/app/clients/?$", page.url):
        wait_for_clients_table(page)
        return

    app_base = page.url.split("/app/")[0]
    page.goto(
        f"{app_base}/app/clients",
        wait_until="domcontentloaded",
        timeout=CLIENTS_PAGE_TIMEOUT,
    )
    page.wait_for_url("**/app/clients", timeout=CLIENTS_PAGE_TIMEOUT, wait_until="domcontentloaded")
    wait_for_clients_table(page)


def open_status_filter(page: Page) -> None:
    wait_for_clients_table(page)
    filters_button = page.locator(".table-actions__filter").first
    status_filter = page.locator('[data-qa*="item-client_data_associated_with_field_filter"]').first
    filters_button.wait_for(state="visible", timeout=CLIENTS_READY_TIMEOUT)
    for attempt in range(3):
        filters_button.click()
        try:
            status_filter.wait_for(state="visible", timeout=FILTER_OPTION_TIMEOUT)
            break
        except PlaywrightTimeoutError:
            if attempt == 2:
                raise
            page.wait_for_timeout(500)
    status_filter.click()


def wait_for_clients_table(page: Page) -> None:
    page.wait_for_url("**/app/clients**", timeout=CLIENTS_PAGE_TIMEOUT, wait_until="domcontentloaded")
    page.locator(".table-actions__filter").first.wait_for(
        state="visible",
        timeout=CLIENTS_READY_TIMEOUT,
    )
    visible_loaders = page.locator(
        ".VcLoader:visible, .vc-loader:visible, "
        ".v-progress-circular:visible, [data-qa='VcLoader']:visible"
    )
    expect(visible_loaders).to_have_count(0, timeout=CLIENTS_READY_TIMEOUT)


def wait_for_client_detail(page: Page, client_name: str) -> None:
    last_error: PlaywrightTimeoutError | None = None
    for attempt in range(2):
        try:
            page.locator('iframe[title="angularjs"]').wait_for(state="visible", timeout=UI_TIMEOUT)
            outer = page.frame_locator('iframe[title="angularjs"]')
            client_name_locators = [
                page.get_by_text(client_name, exact=False),
                outer.get_by_text(client_name, exact=False),
            ]
            if wait_for_any_visible(client_name_locators, timeout=UI_TIMEOUT):
                return
            raise PlaywrightTimeoutError(f"Client detail did not show {client_name}")
        except PlaywrightTimeoutError as exc:
            last_error = exc
            if attempt == 0:
                page.reload(wait_until="domcontentloaded", timeout=CLIENTS_PAGE_TIMEOUT)
                page.wait_for_url("**/app/clients/**", timeout=CLIENTS_PAGE_TIMEOUT, wait_until="domcontentloaded")
    raise last_error or AssertionError(f"Client detail did not load for {client_name}")


def visible_client_names(page: Page) -> list[str]:
    empty_state = page.locator('[data-qa="VcEmptyState"]')
    if empty_state.count() > 0 and empty_state.first.is_visible():
        return []
    names = page.locator('[data-qa="matter-name"]')
    return [names.nth(index).inner_text().strip() for index in range(names.count())]


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
