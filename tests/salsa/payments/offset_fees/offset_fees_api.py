"""API setup helpers for the offset_fees subcategories.

Provisions the prerequisites the legacy `offset-fees.feature` builds `via API`:
- a paid ("suggest to pay") $100 appointment service,
- a client (capturing the client JWT `token` used to open the client portal),
- a past appointment (10th of the previous month) so it shows under the client
  portal "past" bookings tab with a Pay action.

The feature under test (offset fee / surcharge at checkout) stays in the UI;
only these prerequisites are provisioned through the account API.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import time

import requests

# Network timeout for the account setup API (not a UI wait): the integration
# account API can take >5s under load, which otherwise surfaces as setup
# ReadTimeout flakes. UI waits stay capped at 5s elsewhere.
REQUEST_TIMEOUT = 20
# The runner pins the auto-account business and browser context to US Eastern;
# the bookings API treats start_time as UTC, so wall-clock times are localized
# to this zone before conversion.
BUSINESS_TZ = ZoneInfo("America/New_York")
SERVICE_PRICE = "100"


def create_paid_service(context: dict, name: str) -> dict:
    """Create a "suggest to pay" ($100, charge_type=paid) appointment service."""
    payload = {
        "category": {"uid": _get_last_category_uid(context)},
        "staff_data": [{"uid": _get_first_staff_uid(context), "enabled": True}],
        "name": name,
        "service_type": "appointment",
        "currency": "USD",
        "duration": 60,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": "paid",
        "price": SERVICE_PRICE,
        "display": "true",
        "max_attendance": 2,
    }
    response = _account_request(context, "POST", "/v2/settings/services", json=payload)
    service = response.get("data") or response
    if service.get("id") and not service.get("uid"):
        service["uid"] = service["id"]
    return service


def create_client(context: dict, first_name: str, last_name: str, email: str) -> dict:
    """Create a client and capture the top-level JWT `token` (used for CP login)."""
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
    # The client portal JWT is returned alongside the client object, not inside it.
    client["token"] = payload.get("token") or response.get("token")
    if not client.get("token"):
        raise ValueError(f"Client API response did not include a portal token: {response}")
    client["full_name"] = (
        f"{client.get('first_name') or first_name} {client.get('last_name') or last_name}"
    )
    return client


def create_past_appointment(context: dict, service: dict, client: dict) -> dict:
    """Book a past appointment (10th of previous month) carrying the service price.

    A past appointment surfaces under the client portal "past" bookings tab with a
    Pay action, mirroring the legacy `previous_month_10` scheduling date.
    """
    response = _account_request(
        context,
        "POST",
        "/business/scheduling/v1/bookings",
        json={
            "business_id": _get_pivot_uid(context),
            "staff_id": _get_first_staff_uid(context),
            "start_time": _previous_month_tenth().isoformat(),
            "service_id": service.get("id") or service.get("uid"),
            "client_id": client.get("id") or client.get("uid"),
        },
    )
    booking = (response.get("data") or {}).get("booking") or response
    booking_id = booking.get("id") or booking.get("uid")
    if not booking_id:
        raise ValueError(f"Booking response did not include an id: {response}")
    booking["id"] = booking_id
    return booking


def enable_card_and_ach(context: dict) -> None:
    """Enable credit-card and ACH bank-debit checkout via the payment-settings API.

    ACH is a prerequisite (a second payment method is required before the offset-fee
    controls activate), not the feature under test, so it is provisioned via API for
    stability. Mirrors the legacy `allow_credit_card` / `allow_bank_debit_on_checkout`.
    """
    _account_request(
        context,
        "POST",
        "/platform/v1/payment/settings",
        json={
            "payment_settings": {
                "allow_credit_card": True,
                "allow_bank_debit_on_checkout": True,
            }
        },
    )


def unique_email(prefix: str) -> str:
    return f"{prefix}+{int(time.time() * 1000)}@vmeetme.com"


def _previous_month_tenth() -> datetime:
    now = datetime.now()
    year, month = (now.year - 1, 12) if now.month == 1 else (now.year, now.month - 1)
    target = datetime(year, month, 10, 10, 0, tzinfo=BUSINESS_TZ)
    return target.astimezone(timezone.utc)


def _resolve_api_base_url(context: dict) -> str:
    if context.get("api_base_url"):
        return context["api_base_url"].rstrip("/")
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
    retry_allowed = method.upper() in {"GET", "HEAD", "OPTIONS"}
    response = None
    for attempt in range(2):
        try:
            response = requests.request(
                method, url, headers=_account_headers(context), timeout=REQUEST_TIMEOUT, **kwargs
            )
            break
        except (requests.ReadTimeout, requests.ConnectionError):
            if attempt == 1 or not retry_allowed:
                raise
            time.sleep(0.2)
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason} for {url}: {response.text[:500]}",
            response=response,
        )
    return response.json() if response.text else {}


def _get_pivot_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    pivot_uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not pivot_uid:
        raise ValueError("auto_account pivot_uid is missing from context")
    return pivot_uid


def _get_last_category_uid(context: dict) -> str:
    if context.get("offset_fees_category_uid"):
        return context["offset_fees_category_uid"]
    response = _account_request(
        context, "GET", f"/platform/v1/categories?business_id={_get_pivot_uid(context)}"
    )
    categories = response.get("data", {}).get("categories", [])
    if not categories:
        raise ValueError("No service categories returned for auto account")
    context["offset_fees_category_uid"] = categories[-1]["id"]
    return context["offset_fees_category_uid"]


def _get_first_staff_uid(context: dict) -> str:
    if context.get("offset_fees_primary_staff_uid"):
        return context["offset_fees_primary_staff_uid"]
    response = _account_request(
        context, "GET", f"/platform/v1/businesses/{_get_pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for auto account")
    context["offset_fees_primary_staff_uid"] = staffs[0].get("id") or staffs[0].get("uid")
    return context["offset_fees_primary_staff_uid"]
