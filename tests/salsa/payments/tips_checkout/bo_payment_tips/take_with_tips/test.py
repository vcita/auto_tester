# Migrated from automation-js/features/salsa/tips.feature (VCITA2-13899)
# Source: tests/payments/tips_checkout/bo_payment_tips/take_with_tips/script.md

from playwright.sync_api import Page

from tests.salsa.payments.tips_checkout.tips_checkout_bo import (
    assert_payment_page_with_tip,
    close_client_balance,
    record_custom_payment_with_tip,
)


def test_take_with_tips(page: Page, context: dict) -> None:
    """Close balance and record a custom payment, both with tips (BO)."""
    client = context["tips_checkout"]["client"]
    service_name = context["tips_checkout"]["service"]["name"]

    print("  Step 1: Close client balance (record ACH, tip 55%, send receipt)")
    close_client_balance(page, context, client_id=client["id"],
                         record_type="ACH", tip_option="55%", send_receipt=True)
    items = ",".join(sorted([service_name, "package"]))
    assert_payment_page_with_tip(page, context, {
        "client_name": "first last",
        "name": "Payment for Multi-item #0000001",
        "amount": "$387.50",
        "type": "ACH",
        "items": items,
        "tip": "$137.50",
    })

    print("  Step 2: Record custom item 'some_item' $5 with Custom tip 4.5")
    record_custom_payment_with_tip(page, context, client_name="first last",
                                   item_name="some_item", amount="5",
                                   tip_option="Custom", tip_amount="4.5")
    assert_payment_page_with_tip(page, context, {
        "search": "first",
        "name": "Payment for some_item",
        "tip": "$4.50",
    })
