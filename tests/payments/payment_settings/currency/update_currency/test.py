from playwright.sync_api import Page

from tests.payments.payment_settings.payment_settings_api import (
    get_default_currency,
    get_service_currency,
    schedule_meeting,
    set_default_currency,
)


def _schedule_meeting(context: dict) -> dict:
    booking = schedule_meeting(
        context, service=context["currency_service"], client=context["currency_client"],
    )
    if not (booking.get("id") or booking.get("uid")):
        raise AssertionError(f"Meeting was not scheduled (no booking id): {booking}")
    return booking


def _assert_currency(actual: str, expected: str, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def test_update_currency(page: Page, context: dict) -> None:
    service_id = context["currency_service"]["id"]

    print("  Step 1: Assert the default currency is USD")
    _assert_currency(get_default_currency(context), "USD", "initial default currency")
    _assert_currency(get_service_currency(context, service_id), "USD", "initial service currency")

    print("  Step 2: Schedule meeting1 (default currency USD)")
    _schedule_meeting(context)

    print("  Step 3: Set the default currency to EUR (propagated to services)")
    set_default_currency(context, "EUR")

    print("  Step 4: Assert the default currency + service currency read-back is EUR")
    _assert_currency(get_default_currency(context), "EUR", "updated default currency")
    _assert_currency(get_service_currency(context, service_id), "EUR", "updated service currency")

    print("  Step 5: Schedule meeting2 (now reflects EUR)")
    _schedule_meeting(context)
