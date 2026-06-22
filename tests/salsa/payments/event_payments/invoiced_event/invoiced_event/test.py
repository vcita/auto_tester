# Source: tests/payments/event_payments/invoiced_event/invoiced_event/script.md
# Migrated from automation-js/features/salsa/event-payments.feature (VCITA2-13856)

from playwright.sync_api import Page

from tests.salsa.payments.event_payments.event_payments_helpers import (
    assert_invoice_page,
    invoice_event,
    pay_for_invoice,
    search_payments,
)


def test_invoiced_event(page: Page, context: dict) -> None:
    """Invoice the event payment request, pay the invoice ($10), then verify the
    invoice page shows PAID $10.00 and the payment is listed in Payments Received."""
    seeded = context["event_payments"]
    service_name = seeded["service"]["name"]
    client_name = seeded["client"]["name"]
    invoice_name = "event_invoice #0000001"

    print("  Step 1: Invoice the event payment request")
    invoice_event(page, context, invoice_name="event_invoice", billing_address="blablablabla")

    print("  Step 2: Pay the invoice ($10)")
    pay_for_invoice(page, context, invoice_name, "10")

    print("  Step 3: Invoice page shows PAID $10.00")
    assert_invoice_page(page, context, {
        "state": "PAID", "amount": "$10.00", "client_full_name": client_name,
        "service_name": service_name, "invoice_name": invoice_name,
    })

    print("  Step 4: Payments Received shows the invoice payment")
    search_payments(page, context, "first", f"Payment for {invoice_name}", expected_count=1)

    print("  [OK] paying for invoiced event verified")
