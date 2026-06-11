"""API setup helpers for the coupons subcategory.

Creates the prerequisites the legacy `coupons.feature` builds `via API`:
- paid ("suggest to pay") $100 appointment services,
- a client,
- appointments that inherit the service price so each one carries a
  NOT YET DUE payment request the coupon test can discount.

The feature under test (coupon create/apply) stays in the UI; only the
prerequisites are provisioned through the account API.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import time

import requests

# HTTP read timeout for the account setup API. This is a network timeout, not a UI
# wait, so it is deliberately higher than the 5s UI-wait cap: the integration account
# API can take >5s under load, which otherwise surfaces as setup ReadTimeout flakes.
REQUEST_TIMEOUT = 20
# The runner pins both the browser context and the auto-account business to US
# Eastern, and the bookings API treats start_time as UTC, so wall-clock times are
# localized to this zone before conversion.
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
    client["full_name"] = f"{client.get('first_name') or first_name} {client.get('last_name') or last_name}"
    return client


def create_appointment(context: dict, service: dict, client: dict, days_ahead: int) -> dict:
    """Book a future appointment; the booking inherits the service price/charge_type."""
    response = _account_request(
        context,
        "POST",
        "/business/scheduling/v1/bookings",
        json={
            "business_id": _get_pivot_uid(context),
            "staff_id": _get_first_staff_uid(context),
            "start_time": _future_start_time(days_ahead).isoformat(),
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


def unique_email(prefix: str) -> str:
    return f"{prefix}+{int(time.time() * 1000)}@vmeetme.com"


def _future_start_time(days_ahead: int) -> datetime:
    target = (datetime.now() + timedelta(days=days_ahead)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )
    return target.replace(tzinfo=BUSINESS_TZ).astimezone(timezone.utc)


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
    if context.get("coupons_category_uid"):
        return context["coupons_category_uid"]
    response = _account_request(
        context, "GET", f"/platform/v1/categories?business_id={_get_pivot_uid(context)}"
    )
    categories = response.get("data", {}).get("categories", [])
    if not categories:
        raise ValueError("No service categories returned for auto account")
    context["coupons_category_uid"] = categories[-1]["id"]
    return context["coupons_category_uid"]


def _get_first_staff_uid(context: dict) -> str:
    if context.get("coupons_primary_staff_uid"):
        return context["coupons_primary_staff_uid"]
    response = _account_request(
        context, "GET", f"/platform/v1/businesses/{_get_pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for auto account")
    context["coupons_primary_staff_uid"] = staffs[0].get("id") or staffs[0].get("uid")
    return context["coupons_primary_staff_uid"]
