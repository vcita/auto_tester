# Source: tests/payments/event_payments/pay_for_event/pay_event/script.md
# Migrated from automation-js/features/salsa/event-payments.feature (VCITA2-13856)

from playwright.sync_api import Page

from tests.payments.event_payments.event_payments_helpers import (
    assert_cp_conversation_title,
    assert_event_payment_request,
    pay_for_event,
    search_payments,
)


def test_pay_event(page: Page, context: dict) -> None:
    """Pay an event payment request partially ($2 -> DUE $8 of $10) then fully
    ($8 -> PAID $10), verifying Payments Received and the client-portal receipt
    conversation after each."""
    seeded = context["event_payments"]
    service_name = seeded["service"]["name"]
    client_name = seeded["client"]["name"]
    payment_title = f"Payment for {service_name}"

    print("  Step 1: Pay $2 -> DUE $8.00 (out of $10.00)")
    pay_for_event(page, context, "2")
    assert_event_payment_request(page, context, {
        "state": "DUE", "amount": "$8.00 (out of $10.00)",
        "client_full_name": client_name, "service_name": service_name,
    })
    search_payments(page, context, "first", payment_title, expected_count=1)

    print("  Step 2: Pay $8 -> PAID $10.00")
    pay_for_event(page, context, "8")
    assert_event_payment_request(page, context, {
        "state": "PAID", "amount": "$10.00",
        "client_full_name": client_name, "service_name": service_name,
    })
    search_payments(page, context, "first", payment_title, expected_count=2)

    print("  Step 3: Client-portal receipt conversation")
    assert_cp_conversation_title(page, context, f"Thank you for paying: {payment_title}")

    print("  [OK] pay-for-event partial + full verified")
