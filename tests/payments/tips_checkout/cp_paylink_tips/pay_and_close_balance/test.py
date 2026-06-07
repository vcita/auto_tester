# Migrated from automation-js/features/salsa/tips.feature (VCITA2-13899)
# Source: tests/payments/tips_checkout/cp_paylink_tips/pay_and_close_balance/script.md

import time

from playwright.sync_api import Page

from tests.payments.tips_checkout.tips_checkout_bo import assert_payment_page_with_tip
from tests.payments.tips_checkout.tips_checkout_cp import (
    close_balance_via_cp,
    pay_via_payment_form,
)


def test_pay_and_close_balance(page: Page, context: dict) -> None:
    """CP pay-link with a percent tip, then CP close-balance with a custom tip."""
    store = context["tips_checkout"]
    service_name = store["service"]["name"]
    client = store["client"]

    print("  Part A: New client 'steve' pays via public pay link (55% tip)")
    pay_via_payment_form(page, context, pay_for=service_name, amount="100",
                         first_name="steve", email=f"test3+{int(time.time() * 1000)}@vmeetme.com",
                         tip_option="55%")
    assert_payment_page_with_tip(page, context, {
        "search": "steve",
        "client_name": "steve",
        "name": f"Payment for Sale #1 - {service_name}",
        "amount": "$155.00",
        "items": service_name,
        "tip": "$55.00",
    })

    print("  Part B: Existing client 'first last' closes CP balance (custom tip 5)")
    close_balance_via_cp(page, context, portal_token=client["portal_token"], tip_amount="5")
    assert_payment_page_with_tip(page, context, {
        "search": "first",
        "client_name": "first last",
        "name": f"Payment for Sale #2 - {service_name}",
        "amount": "$105.00",
        "items": service_name,
        "tip": "$5.00",
    })
