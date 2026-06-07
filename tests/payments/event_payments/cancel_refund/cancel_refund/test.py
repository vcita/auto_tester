# Source: tests/payments/event_payments/cancel_refund/cancel_refund/script.md
# Migrated from automation-js/features/salsa/event-payments.feature (VCITA2-13856)

from playwright.sync_api import Page

from tests.payments.event_payments.event_payments_helpers import (
    cancel_event_with_refund,
    open_payment_detail_and_assert_title,
    pay_for_event,
)


def test_cancel_refund(page: Page, context: dict) -> None:
    """Pay an event in full ($10), cancel the whole event with a refund, then
    open the refunded payment and assert its detail header (legacy 'payment was
    refunded')."""
    seeded = context["event_payments"]
    service_name = seeded["service"]["name"]

    print("  Step 1: Pay $10 (full)")
    pay_for_event(page, context, "10")

    print("  Step 2: Cancel the event with refund")
    cancel_event_with_refund(page, context)

    print("  Step 3: Payment was refunded (open payment, assert detail title)")
    open_payment_detail_and_assert_title(
        page, context, "first", f"Payment for {service_name}")

    print("  [OK] cancel + refund paid event verified")
