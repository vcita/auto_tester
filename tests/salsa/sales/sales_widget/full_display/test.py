# Source: tests/sales/sales_widget/full_display/script.md
# Migrated from automation-js/features/salsa/sales_widget.feature (VCITA2-13854)

import time

from playwright.sync_api import Page

from tests.account_api import create_client
from tests.salsa.payments.deposits.deposits_api import (
    create_deposit_request,
    create_estimate_via_api,
    create_product,
)
from tests.salsa.sales.sales_widget.sales_widget_helpers import (
    OVERDUE_PAYMENTS,
    PENDING_ESTIMATES,
    TOTAL_REVENUE,
    assert_redirect,
    assert_widget_values,
    create_fee_service,
    create_invoice,
    record_payment,
    schedule_past_appointment,
)

EXPECTED = {
    "total_revenue": "$10.00",
    "pending_estimates": "1",
    "overdue_payments": "$80.00",
    "breakdowns": [
        "1-7 days,1 payments,$10.00",
        "8-30 days,1 payments,$40.00",
        "31+ days,1 payments,$30.00",
    ],
}


def test_full_display(page: Page, context: dict) -> None:
    """Seed a paid invoice ($10), a pending estimate, and three overdue appointment
    fees ($10/$40/$30 at 2/9/35 days past) via API, then assert the Sales widget's
    revenue, pending estimates, overdue payments + age breakdowns, and the
    click-through navigation to the payments / estimates / billing pages."""
    email = f"test+{int(time.time() * 1000)}@vmeetme.com"
    client = create_client(context, "first", "last", email)

    print("  Step 1: Create three 'display a fee' services ($10/$40/$30) via API")
    service_1 = create_fee_service(context, "service_1", 10)
    service_2 = create_fee_service(context, "service_2", 40)
    service_3 = create_fee_service(context, "service_3", 30)

    print("  Step 2: Schedule the three appointments 2/9/35 days in the past (overdue fees)")
    schedule_past_appointment(context, service_1, client, days_ago=2)
    schedule_past_appointment(context, service_2, client, days_ago=9)
    schedule_past_appointment(context, service_3, client, days_ago=35)

    print("  Step 3: Create product21 ($80) and a signature-required estimate with a deposit")
    product = create_product(context, "product21", "80")
    estimate = create_estimate_via_api(
        context, "bestimate", client, [product], is_signature_required=True, send_email=True
    )
    create_deposit_request(context, estimate, amount="10", deposit_type="fixed", total="10")

    print("  Step 4: Create an invoice and record a $10 cash payment (revenue)")
    invoice = create_invoice(
        context, "invoice", client, [{"title": "service_1", "amount": "10", "quantity": 1}]
    )
    record_payment(context, "Payment for invoice", client["id"], "10", invoice["id"], "Invoice")

    print("  Step 5: Sales widget shows total revenue $10, 1 pending estimate, $80 overdue + buckets")
    assert_widget_values(page, context, EXPECTED)

    print("  Step 6: Total revenue -> Payments Received page")
    assert_redirect(page, context, TOTAL_REVENUE, "payments")

    print("  Step 7: Pending estimates -> Estimates page")
    assert_redirect(page, context, PENDING_ESTIMATES, "estimates")

    print("  Step 8: Overdue payments -> Billing & Invoicing page")
    assert_redirect(page, context, OVERDUE_PAYMENTS, "billing")

    print("  [OK] sales widget full display + navigation verified")
