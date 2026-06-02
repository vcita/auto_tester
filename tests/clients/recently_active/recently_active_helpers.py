import time
from datetime import datetime, timedelta, timezone
from typing import Iterable

import requests
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

REQUEST_TIMEOUT = 5
UI_TIMEOUT = 5000
PAGE_READY_TIMEOUT = 5_000
# After each dashboard reload the clients widget loads its rows asynchronously
# (it renders skeletons first). Reading the rows before that load settles is what
# made this test flaky. We wait for the widget to settle before reading, and the
# search index that backs it can lag a beat behind the booking API, so we allow a
# few quick reloads. Every individual wait stays within the 5s cap and there are
# no fixed sleeps - each reload itself gives the index a moment to propagate.
WIDGET_RELOAD_ATTEMPTS = 3
RECENTLY_ACTIVE_VIEW_STORAGE_KEY = "clients-widget-selected-view"


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


def create_service_via_api(context: dict, service_name: str) -> dict:
    category_uid = _get_last_category_uid(context)
    staff_uid = _get_first_staff_uid(context)
    payload = {
        "category": {"uid": category_uid},
        "staff_data": [{"uid": staff_uid, "enabled": True}],
        "name": service_name,
        "service_type": "appointment",
        "currency": "USD",
        "duration": 60,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": "free",
        "display": "true",
        "max_attendance": 2,
    }

    response = _account_request(context, "POST", "/v2/settings/services", json=payload)
    service = response.get("data") or response
    service_id = service.get("id") or service.get("uid")
    if not service_id:
        raise ValueError(f"Service API response did not include an id: {response}")

    return {"id": service_id, "name": service.get("name") or service_name}


def create_appointment_via_api(context: dict, service: dict, client: dict) -> dict:
    payload = {
        "business_id": _get_pivot_uid(context),
        "staff_id": _get_first_staff_uid(context),
        "start_time": _future_start_time(),
        "service_id": service["id"],
        "client_id": client["id"],
    }
    response = _account_request(
        context,
        "POST",
        "/business/scheduling/v1/bookings",
        json=payload,
    )
    data = response.get("data") or response
    return data.get("booking") or data


def prepare_recently_active_clients_view(page: Page, context: dict) -> None:
    view = _get_recently_active_view(context)
    page.evaluate(
        """([key, value]) => localStorage.setItem(key, JSON.stringify(value))""",
        [RECENTLY_ACTIVE_VIEW_STORAGE_KEY, view["uid"]],
    )
    context["recently_active_view_uid"] = view["uid"]
    context["recently_active_view_name"] = view["name"]


def assert_no_recently_active_clients(page: Page) -> None:
    open_dashboard(page)
    if _has_legacy_recently_active_container(page):
        container = _legacy_recently_active_container(page)
        empty_state = container.locator(".empty-state:not(.ng-hide)").first
        empty_state.wait_for(state="visible", timeout=UI_TIMEOUT)
        return

    widget = _new_dashboard_clients_widget(page)
    empty_state = widget.locator('[data-qa="VcEmptyState"]').first
    empty_state.wait_for(state="visible", timeout=UI_TIMEOUT)


def assert_recently_active_clients(page: Page, expected_names: Iterable[str]) -> None:
    expected = list(expected_names)
    last_actual: list[str] = []
    last_error: str | None = None

    for _ in range(WIDGET_RELOAD_ATTEMPTS):
        try:
            open_dashboard(page)
            names = _visible_recently_active_names(page)
            last_actual = names[: len(expected)]
            last_error = None
            if last_actual == expected:
                return
        except PlaywrightTimeoutError as error:
            last_error = str(error).splitlines()[0]

    suffix = f"; last readiness error: {last_error}" if last_error else ""
    raise AssertionError(f"Expected recently active clients {expected}, got {last_actual}{suffix}")


def open_dashboard(page: Page) -> None:
    app_base = _app_base_url(page)
    page.goto(
        f"{app_base}/app/dashboard",
        wait_until="domcontentloaded",
        timeout=PAGE_READY_TIMEOUT,
    )
    page.wait_for_url("**/app/dashboard**", timeout=PAGE_READY_TIMEOUT, wait_until="domcontentloaded")


def _visible_recently_active_names(page: Page) -> list[str]:
    if _has_legacy_recently_active_container(page):
        container = _legacy_recently_active_container(page)
        names = container.locator("div.list-item div.list-item-text div.title-md")
        return [names.nth(index).inner_text().strip() for index in range(names.count())]

    widget = _new_dashboard_clients_widget(page)
    _wait_for_clients_widget_loaded(page)
    items = widget.locator('[data-qa="VcClientItem"]')
    return [_client_item_name(items.nth(index).inner_text()) for index in range(items.count())]


def _wait_for_clients_widget_loaded(page: Page) -> None:
    """Wait until the clients widget finishes its async load before reading rows.

    The widget renders skeletons while fetching; reading rows during that window
    returns an empty list and is what made the test flaky. Settle = no skeletons
    AND a client row or the empty state is present. Capped at UI_TIMEOUT (5s).
    """
    page.wait_for_function(
        """() => {
            const widget = document.querySelector('.clients-widget');
            if (!widget) return false;
            if (widget.querySelector('[data-qa="VcSkeleton"]')) return false;
            return Boolean(
                widget.querySelector('[data-qa="VcClientItem"], [data-qa="VcEmptyState"]')
            );
        }""",
        timeout=UI_TIMEOUT,
    )


def _has_legacy_recently_active_container(page: Page) -> bool:
    for scope in [page, *page.frames]:
        try:
            container = scope.locator(".dashboard-clients-container").first
            if container.count() > 0 and container.is_visible():
                return True
        except Exception:
            continue
    return False


def _legacy_recently_active_container(page: Page):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            try:
                container = scope.locator(".dashboard-clients-container").first
                if container.count() > 0:
                    expect(container).to_be_visible(timeout=UI_TIMEOUT)
                    return container
            except Exception:
                continue
        time.sleep(1)

    raise AssertionError(
        "Legacy recently active clients widget was not found."
    )


def _new_dashboard_clients_widget(page: Page):
    widget = page.locator(".clients-widget").first
    widget.wait_for(state="visible", timeout=PAGE_READY_TIMEOUT)
    widget.locator('[data-qa="VcSelectField"]').first.wait_for(
        state="visible",
        timeout=PAGE_READY_TIMEOUT,
    )
    return widget


def _client_item_name(item_text: str) -> str:
    lines = [line.strip() for line in item_text.splitlines() if line.strip()]
    if not lines:
        return ""
    for line in lines:
        if not (line.isupper() and len(line) <= 3):
            return line
    return lines[0]


def _get_recently_active_view(context: dict) -> dict:
    response = _account_request(context, "GET", "/business/search/v1/views")
    views = response.get("data") or response
    for view in views:
        name = (view.get("name") or "").lower()
        if "recent" in name and ("active" in name or "activity" in name):
            return view

    available_views = [view.get("name") for view in views]
    raise AssertionError(f"Recently active clients view was not found. Available views: {available_views}")


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


def _get_pivot_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    pivot_uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not pivot_uid:
        raise ValueError("auto_account pivot_uid is missing from context")
    return pivot_uid


def _get_last_category_uid(context: dict) -> str:
    response = _account_request(
        context,
        "GET",
        f"/platform/v1/categories?business_id={_get_pivot_uid(context)}",
    )
    categories = response.get("data", {}).get("categories", [])
    if not categories:
        raise ValueError("No service categories returned for auto account")
    return categories[-1]["id"]


def _get_first_staff_uid(context: dict) -> str:
    cached_staff_uid = context.get("recently_active_staff_uid")
    if cached_staff_uid:
        return cached_staff_uid

    response = _account_request(
        context,
        "GET",
        f"/platform/v1/businesses/{_get_pivot_uid(context)}/staffs?status=all",
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for auto account")

    staff_uid = staffs[0].get("id") or staffs[0].get("uid")
    context["recently_active_staff_uid"] = staff_uid
    return staff_uid


def _future_start_time() -> str:
    start_time = datetime.now(timezone.utc) + timedelta(days=30)
    start_time = start_time.replace(minute=0, second=0, microsecond=0)
    return start_time.isoformat().replace("+00:00", "Z")


def _app_base_url(page: Page) -> str:
    if "/app/" in page.url:
        return page.url.split("/app/")[0]

    raise ValueError(f"Cannot infer app base URL from current page URL: {page.url}")
