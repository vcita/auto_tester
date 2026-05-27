import time

import requests
from playwright.sync_api import Page

REQUEST_TIMEOUT = 5
UI_TIMEOUT = 5_000


def create_note_matter_via_api(context: dict) -> dict:
    timestamp = int(time.time())
    client = {
        "first_name": "Note",
        "last_name": f"Matter{timestamp}",
        "email": f"note_matter_{timestamp}@vcita-test.com",
    }
    response = _account_request(
        context,
        "POST",
        "/platform/v1/clients",
        json={**client, "source_name": "automation"},
    )
    payload = response.get("data") or response
    created_client = payload.get("client") or payload
    matter_id = created_client.get("id") or created_client.get("uid")
    if not matter_id:
        raise ValueError(f"Client API response did not include an id: {response}")

    first_name = created_client.get("first_name") or client["first_name"]
    last_name = created_client.get("last_name") or client["last_name"]
    matter_name = f"{first_name} {last_name}".strip()

    context["created_matter_id"] = matter_id
    context["created_matter_name"] = matter_name
    context["created_matter_email"] = created_client.get("email") or client["email"]
    return {
        "id": matter_id,
        "name": matter_name,
        "email": context["created_matter_email"],
    }


def navigate_to_matter_page(page: Page, context: dict, matter_id: str) -> None:
    app_base = _app_base_url(page, context)
    matter_url = f"{app_base}/app/clients/{matter_id}"
    print(f"  [>] Navigating to matter page: {matter_url}")
    page.goto(matter_url, wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    page.wait_for_url("**/app/clients/**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded", timeout=UI_TIMEOUT)


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


def _app_base_url(page: Page, context: dict) -> str:
    if "/app/" in page.url:
        return page.url.split("/app/")[0]

    base_url = context.get("base_url")
    if base_url:
        return base_url.rstrip("/")

    raise ValueError(f"Cannot infer app base URL from current page URL: {page.url}")
