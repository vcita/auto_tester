# Source: tests/sales/adhoc_sale_refund/create_and_refund/script.md
# Migrated from automation-js/features/salsa/sales.feature (VCITA2-13849)

from playwright.sync_api import Page

from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway
from tests.salsa.sales.adhoc_sale_refund.adhoc_sale_helpers import (
    assert_order_in_status,
    assert_payment_in_search,
    assert_payment_success,
    assert_sale_page,
    assert_sale_state,
    open_payment_form,
    pay_via_mock_gateway,
    refund_payment,
)

PAY_FOR = "meeting"
AMOUNT = "20"
AMOUNT_DISPLAY = "$20.00"
SALE_NAME = "Sale #1 - meeting"
PAYMENT_NAME = "Payment for Sale #1 - meeting"


def test_create_and_refund(page: Page, context: dict) -> None:
    """Create an ad-hoc sale via the client-portal payment form (mock gateway),
    verify the paid sale across Orders/Payments/Sale page, then refund it and
    verify the sale becomes CANCELLED."""
    client_email = context["adhoc_client_email"]
    client_first = context.get("adhoc_client_first_name", "first")
    client_name = context.get("adhoc_client_name", "first last")

    print("  Step 1: Connect the mock payment gateway (back office)")
    connect_mock_gateway(page, context)

    print("  Step 2: Open the client-portal make-payment form (meeting, $20)")
    cp_page, cp_context = open_payment_form(page, context, pay_for=PAY_FOR, amount=AMOUNT)
    try:
        print("  Step 3: Pay through the form via the mock gateway")
        pay_via_mock_gateway(cp_page, email=client_email, first_name=client_first)

        print("  Step 4: Verify the payment success page (Payment confirmed, $20.00)")
        assert_payment_success(
            cp_page,
            title="Payment confirmed",
            subtitle="confirmation email",
            amount="Amount received: $20.00",
        )
    finally:
        cp_context.close()

    print("  Step 5: Orders filtered by PAID lists the sale")
    assert_order_in_status(page, context, "Paid", SALE_NAME)

    print("  Step 6: Payments Received search lists the payment")
    assert_payment_in_search(page, context, "first", PAYMENT_NAME)

    print("  Step 7: Sale page shows name, client, PAID, $20.00")
    assert_sale_page(
        page,
        context,
        sale_name=SALE_NAME,
        client_full_name=client_name,
        state="PAID",
        amount=AMOUNT_DISPLAY,
    )

    print("  Step 8: Refund the payment (full)")
    refund_payment(page, "first", PAYMENT_NAME)

    print("  Step 9: Orders filtered by CANCELLED lists the sale; sale state CANCELLED")
    assert_order_in_status(page, context, "Cancelled", SALE_NAME)
    assert_sale_state(page, context, sale_name=SALE_NAME, state="CANCELLED")
    print("  [OK] ad-hoc sale + refund verified")
