# Auto-generated from script.md
# Source: tests/payments/deposits/invoice_deposit_pos/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page

from tests.salsa.payments.deposits.deposits_invoice_ui import (
    assert_invoice_deposit,
    create_invoice_with_deposit,
)
from tests.salsa.payments.deposits.deposits_pos_ui import record_pos_custom_payment


def test_invoice_deposit_pos(page: Page, context: dict) -> None:
    """Record two POS custom-item sales, create and send an invoice with a $50 item,
    assign the Sale #1 payment as the deposit, and verify ISSUED / $45 of $50 / $5."""
    print("  Step 1: POS record - deposit_item $5 (Sale #1)")
    record_pos_custom_payment(page, context, item_name="deposit_item", price="5")

    print("  Step 2: POS record - regular_item1 $3 (Sale #2)")
    record_pos_custom_payment(page, context, item_name="regular_item1", price="3")

    print("  Step 3: Create and send invoice with assigned deposit")
    create_invoice_with_deposit(
        page,
        context,
        title="deposit_invoice",
        item_name="big invoice",
        item_price="50",
        deposit_payment_title="Payment for Sale #1 - deposit_item",
    )

    print("  Step 4: Verify invoice amount, state, and deposit sum")
    assert_invoice_deposit(
        page,
        context,
        amount="$45.00 (out of $50.00)",
        deposit_sum="$5.00",
        state="ISSUED",
    )
    print("  [OK] Invoice deposit (POS) verified")
