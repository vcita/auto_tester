"""API helpers for the Payment Settings migration (VCITA2-13901).

Migrated from automation-js features/salsa/payments_settings.feature. The payment
settings writes the legacy scenarios perform through the Angular/POV settings UI all
resolve to the same Platform endpoint on save, so they are issued directly here
(confirmed against frontage pov paymentSettingsService.js):

  - POST /platform/v1/payment/settings              {payment_settings: {...}}  (save)
  - PUT  /platform/v1/payment/settings/update_default_currency  {}            (propagate currency to services)
  - GET  /platform/v1/payment/settings              -> data.data.payment_settings (read-back)

Each scenario runs on its own isolated account because these settings mutate
account-wide state (currency, credit-card, view-payments) that would otherwise leak
across scenarios.
"""

import requests

from tests.account_api import (
    account_request,
    account_token,
    api_base,
    first_staff_uid,
    future_appointment_start_time,
    pivot_uid,
)

REQUEST_TIMEOUT = 20
# Booking creation occasionally exceeds the shared 5s account-API cap, so the
# scheduling POST gets its own (justified) longer timeout rather than flaking.
SCHEDULE_TIMEOUT = 20


def get_payment_settings(context: dict) -> dict:
    response = account_request(context, "GET", "/platform/v1/payment/settings")
    data = response.get("data") or response
    return data.get("payment_settings") or data


def get_default_currency(context: dict) -> str:
    return (get_payment_settings(context) or {}).get("currency", "")


def save_payment_settings(context: dict, settings: dict) -> dict:
    """POST /platform/v1/payment/settings {payment_settings: settings}."""
    response = account_request(
        context, "POST", "/platform/v1/payment/settings",
        json={"payment_settings": settings},
    )
    data = response.get("data") or response
    return data.get("payment_settings") or data


def set_default_currency(context: dict, currency: str) -> None:
    """Set the default currency and propagate it to existing services.

    Mirrors the POV save path: persist the currency, then PUT update_default_currency
    (empty body) which updates the currency of all existing services (see the
    settings.payments.confirmation.update_default_currency product copy).
    """
    save_payment_settings(context, {"currency": currency})
    requests.put(
        f"{api_base(context)}/platform/v1/payment/settings/update_default_currency",
        json={},
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    ).raise_for_status()


def set_terms_and_policies(context: dict, text: str) -> None:
    """Set custom text terms & policies (terms_and_conditions_type='text')."""
    save_payment_settings(
        context,
        {"terms_and_conditions_type": "text", "terms_and_conditions_value": text},
    )


def get_terms_and_policies(context: dict) -> str:
    return (get_payment_settings(context) or {}).get("terms_and_conditions_value", "")


def set_allow_view_payments(context: dict, allow: bool) -> None:
    """Allow/deny clients viewing their payments in the client portal."""
    save_payment_settings(context, {"allow_view_payments": allow})


def set_allow_credit_card(context: dict, allow: bool) -> None:
    """Enable/disable credit-card payments in the client portal checkout."""
    save_payment_settings(context, {"allow_credit_card": allow})


def schedule_meeting(context: dict, service: dict, client: dict) -> dict:
    """Schedule an appointment (POST /business/scheduling/v1/bookings) with a longer
    timeout than the shared 5s account-API cap (booking creation can run slightly long)."""
    payload = {
        "business_id": pivot_uid(context),
        "staff_id": first_staff_uid(context),
        "start_time": future_appointment_start_time(),
        "service_id": service["id"],
        "client_id": client["id"],
    }
    response = requests.post(
        f"{api_base(context)}/business/scheduling/v1/bookings",
        json=payload,
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=SCHEDULE_TIMEOUT,
    )
    response.raise_for_status()
    body = response.json() if response.text else {}
    data = body.get("data") or body
    return data.get("booking") or data


def get_service(context: dict, service_id: str) -> dict:
    """GET a single service (/v2/settings/services/{id})."""
    response = account_request(context, "GET", f"/v2/settings/services/{service_id}")
    data = response.get("data") or response
    return data.get("service") or data


def get_service_currency(context: dict, service_id: str) -> str:
    return (get_service(context, service_id) or {}).get("currency", "")
