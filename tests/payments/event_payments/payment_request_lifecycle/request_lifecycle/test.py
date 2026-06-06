# Source: tests/payments/event_payments/payment_request_lifecycle/request_lifecycle/script.md
# Migrated from automation-js/features/salsa/event-payments.feature (VCITA2-13856)

from playwright.sync_api import Page

from tests.payments.event_payments.event_payments_helpers import (
    assert_event_payment_request,
    cancel_payment_request,
    edit_payment_request_amount,
)


def test_request_lifecycle(page: Page, context: dict) -> None:
    """Assert the attendee's event payment request is DUE $10, edit it to $50
    (DUE $50), then cancel it (CANCELLED $50)."""
    seeded = context["event_payments"]
    service_name = seeded["service"]["name"]
    client_name = seeded["client"]["name"]

    print("  Step 1: Payment request is DUE $10.00")
    assert_event_payment_request(page, context, {
        "state": "DUE", "amount": "$10.00",
        "client_full_name": client_name, "service_name": service_name,
    })

    print("  Step 2: Edit payment request amount to $50")
    edit_payment_request_amount(page, context, "50")
    assert_event_payment_request(page, context, {
        "state": "DUE", "amount": "$50.00",
        "client_full_name": client_name, "service_name": service_name,
    })

    print("  Step 3: Cancel payment request -> CANCELLED $50.00")
    cancel_payment_request(page, context)
    assert_event_payment_request(page, context, {
        "state": "CANCELLED", "amount": "$50.00",
        "client_full_name": client_name, "service_name": service_name,
    })

    print("  [OK] event payment request lifecycle verified")
