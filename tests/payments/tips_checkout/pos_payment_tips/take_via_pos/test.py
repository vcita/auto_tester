# Migrated from automation-js/features/salsa/tips.feature (VCITA2-13899)
# Source: tests/payments/tips_checkout/pos_payment_tips/take_via_pos/script.md

from playwright.sync_api import Page

from tests.payments.tips_checkout.tips_checkout_bo import assert_payment_page_with_tip
from tests.payments.tips_checkout.tips_checkout_pos import (
    take_custom_item_via_pos,
    take_open_requests_via_pos,
)


def test_take_via_pos(page: Page, context: dict) -> None:
    """Take payment with tips via Point of Sale (open requests + custom item)."""
    service_name = context["tips_checkout"]["service"]["name"]

    print("  Step 1: POS sale from open requests (record ACH, tip 55%)")
    take_open_requests_via_pos(page, context, client_name="first last",
                               record_type="ACH", tip_option="55%")
    items = ",".join(sorted([service_name, "package"]))
    assert_payment_page_with_tip(page, context, {
        "client_name": "first last",
        "name": "Payment for Sale #1 - package (+1 item)",
        "amount": "$387.50",
        "type": "ACH",
        "items": items,
        "tip": "$137.50",
    })

    print("  Step 2: POS custom-item sale (record ACH, Custom tip 4.5)")
    take_custom_item_via_pos(page, context, client_name="first last",
                             item_name="some_item", amount="5",
                             record_type="ACH", tip_option="Custom", tip_amount="4.5")
    assert_payment_page_with_tip(page, context, {
        "search": "first",
        "name": "Payment for Sale #2 - some_item",
        "tip": "$4.50",
    })
