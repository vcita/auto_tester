# Auto-generated from script.md
# Source: tests/payments/deposits/invoice_deposit_quick/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page

from tests.account_api import deny_features
from tests.salsa.payments.deposits.deposits_invoice_ui import (
    assert_invoice_deposit,
    create_invoice_with_deposit,
    record_custom_payment,
    relogin,
)


def test_invoice_deposit_quick(page: Page, context: dict) -> None:
    """Record two payments via Quick Actions, create and send an invoice with a $50 item,
    assign a $5 payment as the deposit, and verify ISSUED / $45 of $50 / $5 deposit."""
    print("  Step 1: Deny point_of_sale and re-login (fresh session picks up the flag)")
    deny_features(context, "point_of_sale")
    relogin(page, context)

    print("  Step 2: Record payment - deposit_item $5 (Quick Actions)")
    record_custom_payment(page, context, item_name="deposit_item", amount="5")

    print("  Step 3: Record payment - regular_item1 $3 (Quick Actions)")
    record_custom_payment(page, context, item_name="regular_item1", amount="3")

    print("  Step 4: Create and send invoice with assigned deposit")
    create_invoice_with_deposit(
        page,
        context,
        title="deposit_invoice",
        item_name="big invoice",
        item_price="50",
        deposit_payment_title="Payment for deposit_item",
    )

    print("  Step 5: Verify invoice amount, state, and deposit sum")
    assert_invoice_deposit(
        page,
        context,
        amount="$45.00 (out of $50.00)",
        deposit_sum="$5.00",
        state="ISSUED",
    )
    print("  [OK] Invoice deposit (Quick Actions) verified")
