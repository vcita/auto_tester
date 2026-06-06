"""API setup helpers for the coupons_checkout subcategory.

Self-contained (mirrors tests/payments/coupons/coupons_api.py) so it does NOT edit
the shared tests/account_api.py — avoiding merge overlap with other in-flight
migrations. Provisions the prerequisites the legacy `coupons-pay.feature` Background
builds via API:
- a 20% tax,
- two "suggest to pay" ($100) appointment services taxed with that tax,
- a client,
- two PAST appointments (legacy `previous_month_10`) that each carry a payable
  balance the client closes in the client portal,
and creates coupons via the API (`POST v2/coupons`, cart or service-scoped).

The feature under test (applying a coupon in CP checkout) stays in the UI; only the
prerequisites are provisioned through the account API.
"""

from __future__ import annotations

import random
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests

# Network timeout for the account setup API (not a UI wait). The integration account
# API can take >5s under load, which would otherwise surface as setup ReadTimeout flakes.
REQUEST_TIMEOUT = 20
# The runner pins both the browser context and the auto-account business to US Eastern,
# and the bookings API treats start_time as UTC, so wall-clock times are localized to
# this zone before conversion (mirrors coupons_api.BUSINESS_TZ).
BUSINESS_TZ = ZoneInfo("America/New_York")
SERVICE_PRICE = "100"
TAX_RATE = "20"
TAX_NAME = "TS"


# --------------------------------------------------------------------------- #
# Account-scoped REST primitive
# --------------------------------------------------------------------------- #
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


def _pivot_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    pivot_uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not pivot_uid:
        raise ValueError("auto_account pivot_uid is missing from context")
    return pivot_uid


def _last_category_uid(context: dict) -> str:
    if context.get("checkout_category_uid"):
        return context["checkout_category_uid"]
    response = _account_request(
        context, "GET", f"/platform/v1/categories?business_id={_pivot_uid(context)}"
    )
    categories = response.get("data", {}).get("categories", [])
    if not categories:
        raise ValueError("No service categories returned for auto account")
    context["checkout_category_uid"] = categories[-1]["id"]
    return context["checkout_category_uid"]


def _first_staff_uid(context: dict) -> str:
    if context.get("checkout_primary_staff_uid"):
        return context["checkout_primary_staff_uid"]
    response = _account_request(
        context, "GET", f"/platform/v1/businesses/{_pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for auto account")
    context["checkout_primary_staff_uid"] = staffs[0].get("id") or staffs[0].get("uid")
    return context["checkout_primary_staff_uid"]


# --------------------------------------------------------------------------- #
# Setup prerequisites
# --------------------------------------------------------------------------- #
def create_tax(context: dict, name: str = TAX_NAME, rate: str = TAX_RATE) -> dict:
    """Create a tax rate (POST business/payments/v1/taxes) and return it (with id/rate)."""
    response = _account_request(
        context,
        "POST",
        "/business/payments/v1/taxes",
        json={
            "tax": {"name": name, "rate": rate, "default_for_categories": []},
            "new_api": True,
        },
    )
    tax = (response.get("data") or response).get("tax") or response.get("data") or response
    tax_id = tax.get("id") or tax.get("uid")
    if not tax_id:
        raise ValueError(f"Tax API response did not include an id: {response}")
    tax["id"] = tax_id
    return tax


def create_taxed_paid_service(context: dict, name: str, tax_ids: list[str]) -> dict:
    """Create a "suggest to pay" ($100, charge_type=paid) appointment service taxed with tax_ids."""
    payload = {
        "category": {"uid": _last_category_uid(context)},
        "staff_data": [{"uid": _first_staff_uid(context), "enabled": True}],
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
        "tax_uids": tax_ids,
    }
    response = _account_request(context, "POST", "/v2/settings/services", json=payload)
    service = response.get("data") or response
    service_id = service.get("id") or service.get("uid")
    if not service_id:
        raise ValueError(f"Service API response did not include an id: {response}")
    return {"id": service_id, "name": service.get("name") or name}


def create_client(context: dict, first_name: str, last_name: str, email: str) -> dict:
    """Create a client and capture its client-portal JWT token (opens the portal as that client)."""
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
    client["id"] = client.get("id") or client.get("uid")
    client["token"] = payload.get("token") or response.get("token")
    client["full_name"] = f"{first_name} {last_name}"
    if not client["id"]:
        raise ValueError(f"Client API response did not include an id: {response}")
    if not client["token"]:
        raise ValueError(f"Client API response did not include a portal token: {response}")
    return client


def _previous_month_day10_utc() -> datetime:
    """Legacy `previous_month_10`: the 10th of the previous month at 10:00 business-time, in UTC.

    Day 10 of the previous month is always strictly before today, so the appointment is
    reliably in the past and shows under the client-portal bookings PAST tab.
    """
    now = datetime.now(BUSINESS_TZ)
    year = now.year if now.month > 1 else now.year - 1
    month = now.month - 1 if now.month > 1 else 12
    local = datetime(year, month, 10, 10, 0, 0, tzinfo=BUSINESS_TZ)
    return local.astimezone(timezone.utc)


def schedule_past_appointment(context: dict, service: dict, client: dict) -> dict:
    """Book a PAST appointment (legacy previous_month_10); it inherits the service price/charge_type
    and produces a payable balance the client closes in the portal."""
    response = _account_request(
        context,
        "POST",
        "/business/scheduling/v1/bookings",
        json={
            "business_id": _pivot_uid(context),
            "staff_id": _first_staff_uid(context),
            "start_time": _previous_month_day10_utc().isoformat(),
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


def create_coupon_via_api(
    context: dict,
    name: str,
    coupon_type: str,
    amount: str,
    *,
    valid_services: list[str] | None = None,
) -> str:
    """Create a coupon (POST v2/coupons) and return its code.

    coupon_type: "percent" or "fixed". valid_services scopes the coupon to specific
    services (None = entire-cart coupon). Mirrors automation-js api/coupons.create_coupon.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "name": name,
        "code": str(random.randint(1000000, 9999999)),
        "coupon_type": coupon_type,
        "amount": amount,
        "starts_at": (now - timedelta(days=1)).isoformat(),
        "expires_at": now.replace(year=now.year + 1).isoformat(),
        "max_redemptions_per_client": None,
        "max_redemptions": None,
        "valid_services": valid_services,
        "valid_staff": None,
    }
    response = _account_request(context, "POST", "/v2/coupons", json=payload)
    coupon = response.get("data") or response
    code = coupon.get("code") or payload["code"]
    if not code:
        raise ValueError(f"Coupon API response did not include a code: {response}")
    return code


def unique_email(prefix: str) -> str:
    return f"{prefix}+{int(time.time() * 1000)}{random.randint(100, 999)}@vmeetme.com"


def provision_paying_client(context: dict, services: dict) -> dict:
    """Create a client and book one PAST appointment per service (appointment_1, appointment_2).

    Each scenario needs its own client + appointments because paying a balance consumes it
    and all four tests share one isolated account. The first booking is issued before the
    second so the client's conversation record exists (the legacy/coupons setup race).
    """
    client = create_client(context, "first", "last", unique_email("test"))
    schedule_past_appointment(context, services["appointment_1"], client)
    schedule_past_appointment(context, services["appointment_2"], client)
    return client
