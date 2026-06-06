# Source: tests/payments/event_payments/cancel_refund/cancel_refund/script.md
# Migrated from automation-js/features/salsa/event-payments.feature (VCITA2-13856)

from playwright.sync_api import Page

from tests.payments.event_payments.event_payments_helpers import (
    cancel_event_with_refund,
    pay_for_event,
    search_payments,
)


def test_cancel_refund(page: Page, context: dict) -> None:
    """Pay an event in full ($10), cancel the whole event with a refund, then
    verify the refunded payment is listed in Payments Received."""
    seeded = context["event_payments"]
    service_name = seeded["service"]["name"]

    print("  Step 1: Pay $10 (full)")
    pay_for_event(page, context, "10")

    print("  Step 2: Cancel the event with refund")
    cancel_event_with_refund(page, context)

    print("  Step 3: Payment was refunded (listed in Payments Received)")
    search_payments(page, context, "first", f"Payment for {service_name}", expected_count=1)

    print("  [OK] cancel + refund paid event verified")
