"""API seeds for the tips_checkout migration (VCITA2-13899).

Mirrors automation-js/features/salsa/tips.feature Background plus per-scenario
prerequisites that are NOT the behaviour under test: the ``tips`` app, tips
settings (tip options + BO/CP enable flags), services, packages, scheduled
appointments/events, invoices, and base payments. The tipping UI actions
themselves (BO close-balance / POS / CP / follow-up tip dialogs) stay in the
test bodies via the ``tips_checkout_bo`` / ``tips_checkout_pos`` /
``tips_checkout_cp`` helpers.

Translation notes:
- Legacy "user set tips settings via API" did ``PUT /v2/settings`` with top-level
  ``tips`` + ``enable_tips_for_bo``/``enable_tips_for_cp``. auto_tester proved a flat
  ``PUT /v2/settings`` returns 200 but drops ``tips`` (see tips_settings/tips_account),
  so we use the POV Save route ``POST /platform/v1/payment/settings`` with
  ``payment_settings: {tips, enable_tips_for_bo, enable_tips_for_cp}`` and confirm
  persistence with an independent GET read-back.
- ``previous_month_10`` (a past meeting date) is computed so the service/package
  requests are immediately payable, mirroring the legacy near-now scheduling.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import requests

from tests.account_api import (
    REQUEST_TIMEOUT,
    account_request,
    account_token,
    admin_headers,
    api_base,
    assign_package_to_client,
    create_appointment_via_api,
    create_client,
    create_package_via_api,
    create_service_via_api,
    deny_features,
    enable_features,
    pivot_uid,
)

PAYMENT_SETTINGS_PATH = "/platform/v1/payment/settings"
PERSIST_POLL_SECONDS = 10
PERSIST_POLL_INTERVAL = 0.5

# Tips feature flags shared by every tips_checkout scenario. tips_settings gates the
# tip picker; the checkout/follow-up flags expose POS / CP / follow-up tip surfaces.
TIPS_FLAGS = (
    "rollout.payments.tips_settings,rollout.payments.gateway_platform,"
    "rollout.payments.tips_checkout_v2,follow_up_tip,bo_follow_up_tip,"
    "client_portal_checkout_v2"
)


def _store(context: dict) -> dict:
    return context.setdefault("tips_checkout", {})


def directory_uid(context: dict) -> str:
    value = context.get("directory_id") or context.get("directory_uid")
    if not value:
        raise ValueError("directory_id missing from context for app assignment")
    return value


def assign_app(context: dict, app_code: str) -> None:
    """Assign a platform app (e.g. ``tips``) to the account business via API.

    Mirrors legacy ``admin assigns app "tips"`` -> POST /platform/v1/apps/{app}/assign
    with **Admin** auth (the assign endpoint rejects the account Bearer token with 401).
    """
    response = requests.post(
        f"{api_base(context)}/platform/v1/apps/{app_code}/assign",
        json={"business_uid": pivot_uid(context), "directoryUid": directory_uid(context)},
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()


# --------------------------------------------------------------------------- #
# Tips settings (POV payment-settings route + read-back)
# --------------------------------------------------------------------------- #
def _read_payment_settings(context: dict) -> dict:
    response = requests.get(
        f"{api_base(context)}{PAYMENT_SETTINGS_PATH}",
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json().get("data", {}).get("payment_settings", {}) or {}


def _post_tips(context: dict, values: list, enable_bo: bool, enable_cp: bool) -> None:
    payment_settings: dict = {
        "tips": [{"type": "percent", "value": int(v)} for v in values]
    }
    if enable_bo:
        payment_settings["enable_tips_for_bo"] = True
    if enable_cp:
        payment_settings["enable_tips_for_cp"] = True
    requests.post(
        f"{api_base(context)}{PAYMENT_SETTINGS_PATH}",
        json={"payment_settings": payment_settings},
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    ).raise_for_status()


def set_tips(context: dict, values: list, *, enable_bo: bool = False,
             enable_cp: bool = False) -> None:
    """Persist tip options + BO/CP enable flags, confirmed by an independent GET read.

    The payment-settings write can lag, so the POST is retried once if the read-back
    has not caught up (same pattern as tips_settings/tips_account.set_tips_via_api)."""
    expected = [int(v) for v in values]
    _post_tips(context, values, enable_bo, enable_cp)
    deadline = time.monotonic() + PERSIST_POLL_SECONDS
    reposted = False
    last: dict = {}
    while time.monotonic() < deadline:
        last = _read_payment_settings(context)
        tips_ok = [int(t["value"]) for t in (last.get("tips") or []) if t.get("value") is not None] == expected
        bo_ok = (not enable_bo) or bool(last.get("enable_tips_for_bo"))
        cp_ok = (not enable_cp) or bool(last.get("enable_tips_for_cp"))
        if tips_ok and bo_ok and cp_ok:
            return
        time.sleep(PERSIST_POLL_INTERVAL)
        if not reposted and time.monotonic() > deadline - PERSIST_POLL_SECONDS / 2:
            _post_tips(context, values, enable_bo, enable_cp)
            reposted = True
    raise AssertionError(
        f"Tips settings not persisted after {PERSIST_POLL_SECONDS}s: GET payment_settings="
        f"{{tips: {last.get('tips')}, bo: {last.get('enable_tips_for_bo')}, "
        f"cp: {last.get('enable_tips_for_cp')}}}, expected tips {expected} bo={enable_bo} cp={enable_cp}"
    )


# --------------------------------------------------------------------------- #
# Shared seed: tips app + BO tips + service/package/appointment for a client
# --------------------------------------------------------------------------- #
def seed_balance_tip_account(context: dict, *, deny_pos: bool) -> dict:
    """Common API seed for the BO close-balance and POS tip scenarios.

    tips app + 55/66/77 tips enabled for BO, a suggest-to-pay $100 ``service``, a
    specific $150 ``package`` (2x service) assigned to a fresh ``first last`` client,
    and a past appointment - so the close-balance / POS sale has a payable balance.
    ``deny_pos`` denies point_of_sale for the BO close-balance scenario (legacy
    dialogs) and leaves it enabled for the POS scenario. Returns the tips_checkout
    store. The caller must log in AFTER this seed so the Angular Account model loads
    the tips (``showTips`` is computed from Account.settings at login)."""
    if deny_pos:
        deny_features(context, "point_of_sale")
    enable_features(context, TIPS_FLAGS)
    assign_app(context, "tips")
    set_tips(context, [55, 66, 77], enable_bo=True)

    store = _store(context)
    client = create_client(context, "first", "last", f"test+{int(time.time() * 1000)}@vmeetme.com")
    store["client"] = {"id": client["id"], "name": "first last", "email": client["email"],
                       "portal_token": client.get("token")}

    service = create_service_via_api(context, "service", charge_type="paid", price="100")
    service["price"] = "100"
    store["service"] = service

    package = create_package_via_api(
        context, "package",
        services=[{"id": service["id"], "name": service["name"], "price": "100", "currency": "USD"}],
        total_bookings=2, price="150",
    )
    assign_package_to_client(context, store["client"]["id"], package["id"], "150")
    store["package"] = package

    create_appointment_via_api(context, service, {"id": store["client"]["id"]},
                               start_time=previous_month_day10_start())
    return store


def seed_cp_tip_account(context: dict) -> dict:
    """API seed for the CP pay-link tip scenario.

    tips app + 55/66/77 tips enabled for CP, a suggest-to-pay $100 ``service``, a fresh
    ``first last`` client (portal token kept for the CP close-balance action), and a
    past appointment for that client so it has a payable CP balance. The mock gateway
    must still be connected (UI) by the caller, and the caller logs in for that step."""
    enable_features(context, TIPS_FLAGS)
    assign_app(context, "tips")
    set_tips(context, [55, 66, 77], enable_cp=True)

    store = _store(context)
    service = create_service_via_api(context, "service", charge_type="paid", price="100")
    service["price"] = "100"
    store["service"] = service

    client = create_client(context, "first", "last", f"test+{int(time.time() * 1000)}@vmeetme.com")
    store["client"] = {"id": client["id"], "name": "first last", "email": client["email"],
                       "portal_token": client.get("token")}

    create_appointment_via_api(context, service, {"id": store["client"]["id"]},
                               start_time=previous_month_day10_start())
    return store


def seed_cp_followup_tip_account(context: dict) -> dict:
    """API seed for the CP follow-up-tip scenario.

    tips app + 55/66/77 tips enabled for CP, a require-to-pay ``require`` ($100) and a
    suggest-to-pay ``suggest`` ($50) service, a ``first last`` client (portal token kept),
    a past appointment for each service, and a recorded $100 Cash payment for the
    ``require`` meeting so it is fully paid - the prerequisite for the CP "Add a tip"
    follow-up action. The mock gateway is connected (UI) by the caller, which logs in."""
    enable_features(context, TIPS_FLAGS)
    assign_app(context, "tips")
    set_tips(context, [55, 66, 77], enable_cp=True)

    store = _store(context)
    client = create_client(context, "first", "last", f"test+{int(time.time() * 1000)}@vmeetme.com")
    store["client"] = {"id": client["id"], "name": "first last", "email": client["email"],
                       "portal_token": client.get("token")}

    require = create_service_via_api(context, "require", charge_type="paid_force", price="100")
    suggest = create_service_via_api(context, "suggest", charge_type="paid", price="50")
    store["require_service"] = require
    store["suggest_service"] = suggest

    require_booking = create_appointment_via_api(context, require, {"id": store["client"]["id"]},
                                                 start_time=previous_month_day10_start())
    create_appointment_via_api(context, suggest, {"id": store["client"]["id"]},
                               start_time=previous_month_day20_start())
    require_booking_id = require_booking.get("id") or require_booking.get("uid")

    create_payment_via_api(context, title="Payment for require",
                           client_id=store["client"]["id"], amount="100",
                           subject_type="Meeting", subject_id=require_booking_id)
    store["require_meeting_name"] = require["name"]
    return store


# --------------------------------------------------------------------------- #
# Dates
# --------------------------------------------------------------------------- #
def _previous_month_day_start(day: int) -> str:
    today = datetime.now(timezone.utc)
    first_of_this_month = today.replace(day=1)
    last_prev = first_of_this_month - timedelta(days=1)
    start = last_prev.replace(day=day, hour=12, minute=0, second=0, microsecond=0)
    return start.isoformat().replace("+00:00", "Z")


def previous_month_day10_start() -> str:
    """ISO start_time for the 10th of the previous month at noon UTC (legacy
    ``previous_month_10`` -> a payable, completed-able past meeting)."""
    return _previous_month_day_start(10)


def previous_month_day20_start() -> str:
    """ISO start_time for the 20th of the previous month at noon UTC (legacy
    ``previous_month_20``)."""
    return _previous_month_day_start(20)


# --------------------------------------------------------------------------- #
# Invoices + payments (scenarios 4/5/6)
# --------------------------------------------------------------------------- #
def create_invoice_via_api(context: dict, *, title: str, client_id: str,
                           items: list[dict], billing_address: str = "") -> dict:
    """Create an invoice via API (mirrors legacy api/invoices.create_invoice).

    ``items`` entries: {product_name, description, price, save_item?}. Returns the
    created invoice including its generated title (e.g. ``invoice #0000001``)."""
    today = datetime.now(timezone.utc).date().isoformat()
    payload = {
        "title": title,
        "client_id": client_id,
        "address": billing_address,
        "currency": "USD",
        "due_date": today,
        "issued_at": today,
        "items": [
            {
                "title": item["product_name"],
                "amount": item["price"],
                "description": item.get("description", ""),
                "quantity": 1,
            }
            for item in items
        ],
        "send_email": False,
        "allow_online_payment": False,
    }
    response = account_request(context, "POST", "/platform/v1/invoices", json=payload)
    data = response.get("data") or response
    invoice = data.get("invoice") or data
    invoice["title"] = invoice.get("title") or title
    return invoice


def create_payment_via_api(context: dict, *, title: str, client_id: str, amount: str | int,
                           subject_type: str, subject_id: str,
                           payment_method: str = "Cash") -> dict:
    """Create a recorded payment via API (mirrors legacy api/payments.create_payment)."""
    payload = {
        "title": title,
        "client_id": client_id,
        "amount": amount,
        "currency": "USD",
        "payment_method": payment_method,
        "payment_subject_id": subject_id,
        "payment_subject_type": subject_type,
    }
    response = account_request(context, "POST", "/platform/v1/payments", json=payload)
    data = response.get("data") or response
    return data.get("payment") or data


# --------------------------------------------------------------------------- #
# Scenario 5 seed: invoice + paid payment (BO follow-up charge tip)
# --------------------------------------------------------------------------- #
def seed_invoice_followup_tip_account(context: dict) -> dict:
    """API seed for the invoice follow-up-tip (BO charge) scenario.

    tips app + 10/20/30 tips enabled for BO, a ``first last`` client, an invoice with a
    saved ``product_item200`` line ($20), and a recorded $20 Cash payment for that invoice
    so it is fully paid - the prerequisite for the invoice "Add a tip" follow-up action.
    The mock gateway is connected (UI) by the caller (required for the charge tip)."""
    enable_features(context, TIPS_FLAGS)
    assign_app(context, "tips")
    set_tips(context, [10, 20, 30], enable_bo=True)

    store = _store(context)
    client = create_client(context, "first", "last", f"test+{int(time.time() * 1000)}@vmeetme.com")
    store["client"] = {"id": client["id"], "name": "first last", "email": client["email"]}

    invoice = create_invoice_via_api(
        context, title="invoice", client_id=client["id"], billing_address="persepolis, persia",
        items=[{"product_name": "product_item200", "description": "short desc", "price": "20"}],
    )
    store["invoice"] = invoice
    create_payment_via_api(context, title=f"Payment for {invoice['title']}",
                           client_id=client["id"], amount="20",
                           subject_type="Invoice", subject_id=invoice["id"])
    return store


# --------------------------------------------------------------------------- #
# Scenario 6 seed: event + registered attendee + paid attendance (BO record tip)
# --------------------------------------------------------------------------- #
def _register_attendee(context: dict, event_uid: str, client_id: str, email: str) -> str:
    """Register a client on an event and return their event-attendance id."""
    response = account_request(
        context, "POST",
        f"/v2/event_instances/{event_uid}/event_attendances/bulk_create",
        json={"client_ids": [client_id], "invite_message": None,
              "applySeries": False, "apply_on_series": False},
    )
    data = response if isinstance(response, list) else response.get("data", response)
    attendances = data if isinstance(data, list) else (
        data.get("event_attendances") or data.get("attendances") or data.get("attendees") or [])
    for attendance in attendances:
        client = attendance.get("client") or {}
        if client.get("email") == email or attendance.get("client_id") == client_id:
            attendance_id = attendance.get("id") or attendance.get("uid")
            if attendance_id:
                return attendance_id
    raise ValueError(f"Could not resolve event-attendance id from bulk_create response: {response}")


def seed_event_followup_tip_account(context: dict) -> dict:
    """API seed for the event follow-up-tip (BO record) scenario.

    tips app + 10/20/30 tips enabled for BO, a ``first last`` client, a require-to-pay
    ``r2p_event`` event with the client registered, and a recorded $10 Cash payment for
    that attendance so it is fully paid - the prerequisite for the event "Add a tip"
    follow-up action."""
    from tests.salsa.payments.event_payments.event_payments_api import (
        create_event_service,
        schedule_event,
    )

    enable_features(context, TIPS_FLAGS)
    assign_app(context, "tips")
    set_tips(context, [10, 20, 30], enable_bo=True)

    store = _store(context)
    client = create_client(context, "first", "last", f"test+{int(time.time() * 1000)}@vmeetme.com")
    store["client"] = {"id": client["id"], "name": "first last", "email": client["email"]}

    service = create_event_service(context, "r2p_event", 10)
    event = schedule_event(context, service)
    store["event_name"] = event["name"]
    store["event_uid"] = event["uid"]
    attendance_id = _register_attendee(context, event["uid"], client["id"], client["email"])
    payment = create_payment_via_api(context, title="Payment for r2p_event",
                                     client_id=client["id"], amount="10",
                                     subject_type="EventAttendance", subject_id=attendance_id)
    store["event_payment_id"] = payment.get("id") or payment.get("uid")
    return store
