import time

import requests
from playwright.sync_api import Page

from tests._functions.login.test import fn_login

REQUEST_TIMEOUT = 30
SERVICE_PRICE = "100"
PRODUCT_PRICE = "10"
PRODUCT_DESCRIPTION = "description for payable item2"
TAX_RATE = "13"


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


def _account_request(context: dict, method: str, path: str, **kwargs) -> dict:
    url = f"{_resolve_api_base_url(context)}{path}"
    response = requests.request(
        method, url, headers=_account_headers(context), timeout=REQUEST_TIMEOUT, **kwargs
    )
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason} for {url}: {response.text[:500]}",
            response=response,
        )
    return response.json()


def _pivot_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    pivot_uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not pivot_uid:
        raise ValueError("auto_account pivot_uid is missing from context")
    return pivot_uid


def _create_priced_service(context: dict) -> None:
    timestamp = int(time.time())
    service_name = f"service {timestamp}"

    categories = _account_request(
        context, "GET", f"/platform/v1/categories?business_id={_pivot_uid(context)}"
    )
    category_uid = categories.get("data", {}).get("categories", [{}])[-1].get("id")

    staffs = _account_request(
        context, "GET", f"/platform/v1/businesses/{_pivot_uid(context)}/staffs?status=all"
    )
    staff_uid = staffs.get("data", {}).get("staff", [{}])[0].get("id")

    payload = {
        "category": {"uid": category_uid},
        "staff_data": [{"uid": staff_uid, "enabled": True}],
        "name": service_name,
        "service_type": "appointment",
        "currency": "USD",
        "duration": 60,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": "paid_force",
        "price": SERVICE_PRICE,
        "display": "true",
        "max_attendance": 2,
    }
    _account_request(context, "POST", "/v2/settings/services", json=payload)

    context["sales_service_name"] = service_name
    context["sales_service_price"] = SERVICE_PRICE


def _create_product(context: dict) -> None:
    timestamp = int(time.time())
    product_name = f"product2 {timestamp}"
    payload = {
        "product": {
            "name": product_name,
            "description": PRODUCT_DESCRIPTION,
            "price": PRODUCT_PRICE,
            "currency": "USD",
            "display": True,
        },
        "new_api": True,
    }
    _account_request(context, "POST", "/business/payments/v1/products", json=payload)

    context["sales_product_name"] = product_name
    context["sales_product_description"] = PRODUCT_DESCRIPTION
    context["sales_product_price"] = PRODUCT_PRICE


def _create_tax(context: dict) -> None:
    timestamp = int(time.time())
    tax_name = f"TS{timestamp}"
    payload = {"tax": {"name": tax_name, "rate": TAX_RATE}, "new_api": True}
    _account_request(context, "POST", "/business/payments/v1/taxes", json=payload)

    context["sales_tax_name"] = tax_name
    context["sales_tax_rate"] = TAX_RATE


def setup_sales(page: Page, context: dict) -> None:
    """
    Setup for the Sales category (estimates).

    Logs in and creates the shared catalog used by all estimate tests:
    a priced service ($100), a product ($10) and a tax (13%). Each estimate
    test creates its own client at runtime so the search-by-client assertion
    stays isolated.

    Saves to context:
    - sales_service_name / sales_service_price
    - sales_product_name / sales_product_description / sales_product_price
    - sales_tax_name / sales_tax_rate
    """
    username = context.get("username")
    password = context.get("password")
    if not username or not password:
        raise ValueError(
            "username and password not in context. Set target.auth.username and "
            "target.auth.password in config.yaml."
        )

    print("  Step 1: Logging in...")
    fn_login(page, context, username=username, password=password)

    print("  Step 2: Creating priced service via API...")
    _create_priced_service(context)

    print("  Step 3: Creating product via API...")
    _create_product(context)

    print("  Step 4: Creating tax via API...")
    _create_tax(context)

    print(
        f"  Sales setup complete - service={context['sales_service_name']}, "
        f"product={context['sales_product_name']}, tax={context['sales_tax_name']}"
    )
