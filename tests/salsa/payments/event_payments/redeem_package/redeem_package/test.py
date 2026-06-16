# Source: tests/payments/event_payments/redeem_package/redeem_package/script.md
# Migrated from automation-js/features/salsa/event-payments.feature (VCITA2-13856)

from playwright.sync_api import Page

from tests.salsa.payments.event_payments.event_payments_helpers import (
    assert_event_payment_request,
    redeem_with_package,
)


def test_redeem_package(page: Page, context: dict) -> None:
    """Redeem the attendee's event payment request with their package, then verify
    the payment request is PAID for $0.00."""
    seeded = context["event_payments"]
    service_name = seeded["service"]["name"]
    client_name = seeded["client"]["name"]

    print("  Step 1: Redeem the event payment request with the package")
    redeem_with_package(page, context)

    print("  Step 2: Payment request is PAID $0.00")
    assert_event_payment_request(page, context, {
        "state": "PAID", "amount": "$0.00",
        "client_full_name": client_name, "service_name": service_name,
    })

    print("  [OK] event payment request redeemed with package")
