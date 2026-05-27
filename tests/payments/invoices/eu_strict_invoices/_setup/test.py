import time

import requests
from playwright.sync_api import Page

from tests._functions.login.test import fn_login

REQUEST_TIMEOUT = 30
SERVICE_PRICE = "100"


def _resolve_api_base_url(context: dict) -> str:
    api_base_url = context.get("api_base_url")
    if api_base_url:
        return api_base_url.rstrip("/")
    raise ValueError("api_base_url is missing from context")


def _account_headers(context: dict) -> dict:
    auto_account = context.get("auto_account") or {}
    token = auto_account.get("api_token") or auto_account.get("auth_token")
    if not token:
        raise ValueError("auto_account api_token is missing from context")
    return {"Authorization": f"Bearer {token}"}


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


def _business_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not uid:
        raise ValueError("auto_account pivot_uid is missing from context")
    return uid


def _get_last_category_uid(context: dict) -> str:
    response = _account_request(
        context,
        "GET",
        f"/platform/v1/categories?business_id={_business_uid(context)}",
    )
    categories = response.get("data", {}).get("categories", [])
    if not categories:
        raise ValueError("No service categories returned for isolated account")
    return categories[-1]["id"]


def _get_first_staff_uid(context: dict) -> str:
    response = _account_request(
        context,
        "GET",
        f"/platform/v1/businesses/{_business_uid(context)}/staffs?status=all",
    )
    staff = response.get("data", {}).get("staff", [])
    if not staff:
        raise ValueError("No staff returned for isolated account")
    return staff[0].get("id") or staff[0].get("uid")


def _create_client(context: dict) -> None:
    timestamp = int(time.time())
    response = _account_request(
        context,
        "POST",
        "/platform/v1/clients",
        json={
            "first_name": "first",
            "last_name": "last",
            "email": f"test+{timestamp}@vmeetme.com",
            "address": "Rome, Italy",
            "source_name": "automation",
        },
    )
    payload = response.get("data") or response
    client = payload.get("client") or payload
    client_id = client.get("id") or client.get("uid")
    if not client_id:
        raise ValueError(f"Client API response did not include an id: {response}")

    context["created_client_id"] = client_id
    context["created_client_name"] = "first last"
    context["created_client_email"] = client.get("email")
    context["invoice_client_search_term"] = "first last"


def _create_paid_service(context: dict) -> None:
    timestamp = int(time.time())
    service_name = f"service{timestamp}"
    payload = {
        "category": {"uid": _get_last_category_uid(context)},
        "staff_data": [{"uid": _get_first_staff_uid(context), "enabled": True}],
        "name": service_name,
        "service_type": "appointment",
        "currency": "USD",
        "duration": 60,
        "interaction_type": "business_location",
        "meeting_interaction_details": "Rome, Italy",
        "charge_type": "paid_non_secured",
        "price": SERVICE_PRICE,
        "display": "true",
        "max_attendance": 2,
    }
    response = _account_request(context, "POST", "/v2/settings/services", json=payload)
    payload_data = response.get("data") or response
    service = payload_data.get("service") or payload_data

    context["invoice_service"] = service
    context["invoice_service_name"] = service.get("name") or service_name
    context["invoice_service_price"] = SERVICE_PRICE


def setup_eu_strict_invoices(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not username or not password:
        raise ValueError("Isolated account username and password are missing from context")

    fn_login(page, context, username=username, password=password)
    _create_client(context)
    _create_paid_service(context)
