# Source: tests/payments/event_payments/pay_via_pos/pay_pos/script.md
# Migrated from automation-js/features/salsa/event-payments.feature (VCITA2-13856)

from playwright.sync_api import Page

from tests.payments.event_payments.event_payments_helpers import (
    assert_cp_conversation_title,
    assert_order_in_status,
    assert_sale_page,
    record_event_payment_via_pos,
    search_payments,
)


def test_pay_pos(page: Page, context: dict) -> None:
    """Pay the event payment request through Point of Sale (record-payment), then
    verify the resulting Sale across Orders, the Sale page, Payments Received, and
    the client-portal conversation."""
    seeded = context["event_payments"]
    service_name = seeded["service"]["name"]
    client_name = seeded["client"]["name"]
    sale_name = f"Sale #1 - {service_name}"

    print("  Step 1: Record-payment via Point of Sale")
    record_event_payment_via_pos(page, context)

    print(f"  Step 2: Orders shows PAID '{sale_name}'")
    assert_order_in_status(page, context, "PAID", sale_name)

    print("  Step 3: Sale page shows PAID $10.00")
    assert_sale_page(page, context, {
        "sale_name": sale_name, "client_full_name": client_name,
        "state": "PAID", "amount": "$10.00",
    })

    print("  Step 4: Payments Received shows the sale payment")
    search_payments(page, context, "first", f"Payment for {sale_name}", expected_count=1)

    print("  Step 5: Client-portal conversation receipt")
    assert_cp_conversation_title(page, context, f"Payment for {service_name}")

    print("  [OK] pay-for-event via POS verified")
