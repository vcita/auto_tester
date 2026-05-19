from playwright.sync_api import Page
import requests
import time

from tests._functions.login.test import fn_login

REQUEST_TIMEOUT = 30
PAYMENT_SERVICE_PRICE = "100"


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
        method,
        url,
        headers=_account_headers(context),
        timeout=REQUEST_TIMEOUT,
        **kwargs,
    )
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason} for {url}: {response.text[:500]}",
            response=response,
        )
    return response.json()


def _get_last_category_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    pivot_uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not pivot_uid:
        raise ValueError("auto_account pivot_uid is missing from context")

    response = _account_request(
        context,
        "GET",
        f"/platform/v1/categories?business_id={pivot_uid}",
    )
    categories = response.get("data", {}).get("categories", [])
    if not categories:
        raise ValueError("No service categories returned for auto account")
    return categories[-1]["id"]


def _get_first_staff_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    pivot_uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not pivot_uid:
        raise ValueError("auto_account pivot_uid is missing from context")

    response = _account_request(
        context,
        "GET",
        f"/platform/v1/businesses/{pivot_uid}/staffs?status=all",
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for auto account")

    return staffs[0].get("id") or staffs[0].get("uid")


def _create_required_payment_service(context: dict) -> None:
    timestamp = int(time.time())
    service_name = f"Invoice Paid Service {timestamp}"
    category_uid = _get_last_category_uid(context)
    staff_uid = _get_first_staff_uid(context)

    payload = {
        "category": {"uid": category_uid},
        "staff_data": [
            {
                "uid": staff_uid,
                "enabled": True,
            }
        ],
        "name": service_name,
        "service_type": "appointment",
        "currency": "USD",
        "duration": 60,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": "paid_force",
        "price": PAYMENT_SERVICE_PRICE,
        "display": "true",
        "max_attendance": 2,
    }

    response = _account_request(context, "POST", "/v2/settings/services", json=payload)
    service = response.get("data") or response

    context["invoice_service"] = service
    context["invoice_service_name"] = service.get("name") or service_name
    context["invoice_service_price"] = PAYMENT_SERVICE_PRICE


def _create_invoice_picker_client(context: dict) -> None:
    timestamp = int(time.time())
    first_name = "Appt"
    last_name = "TestClient"
    email = f"test_{timestamp}@vcita-test.com"

    response = _account_request(
        context,
        "POST",
        "/platform/v1/clients",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "source_name": "automation",
        },
    )
    payload = response.get("data") or response
    client = payload.get("client") or payload
    client_id = client.get("id") or client.get("uid")
    if not client_id:
        raise ValueError(f"Client API response did not include an id: {response}")

    full_name = f"{client.get('first_name') or first_name} {client.get('last_name') or last_name}"
    context["created_client_id"] = client_id
    context["created_client_name"] = full_name
    context["created_client_email"] = client.get("email") or email
    context["invoice_client_search_term"] = full_name

    print(f"  [OK] Created client: {full_name}")
    print(f"       Email: {context['created_client_email']}")
    print(f"       Client ID: {client_id}")


def setup_payments(page: Page, context: dict) -> None:
    """
    Setup for payments category tests.

    Logs in and creates the client required by invoice picker flows.

    Credentials: from context (injected by runner from config.yaml target.auth). No fallbacks.

    Saves to context:
    - logged_in_user: The username that was logged in
    - created_client_id: ID of the client used by invoice flows
    - created_client_name: Full name used by invoice picker flows
    - created_client_email: Email of the invoice picker client
    - invoice_client_search_term: Search term used by invoice picker flows
    """
    username = context.get("username")
    password = context.get("password")
    if not username or not password:
        raise ValueError(
            "username and password not in context. Set target.auth.username and target.auth.password in config.yaml."
        )

    # Step 1: Login
    print("  Step 1: Logging in...")
    fn_login(page, context, username=username, password=password)

    print("  Step 2: Creating invoice picker client...")
    _create_invoice_picker_client(context)

    print("  Step 3: Creating required-payment invoice service via API...")
    _create_required_payment_service(context)

    print("  Payments setup complete - user is logged in")
