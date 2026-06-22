"""Apply a cart fixed-amount coupon in the client-portal checkout.

Migrates automation-js features/salsa/coupons-pay.feature
(scenario: Client apply cart fixed amount coupon in cp checkout).
"""

from playwright.sync_api import Page

from tests.salsa.payments.coupons_checkout.coupons_checkout_api import (
    create_coupon_via_api,
    provision_paying_client,
)
from tests.salsa.payments.coupons_checkout.coupons_checkout_cp import (
    assert_payment_success,
    open_portal,
    pay_meeting_with_coupon,
)

CONFIRMED_TITLE = "Payment confirmed"
CONFIRMED_SUBTITLE = "A confirmation email is on its way to your inbox"
EXPECTED_AMOUNT = "Amount received: $84.00"


def test_cart_fixed(page: Page, context: dict) -> None:
    services = context["checkout_services"]

    print("  Step 1: Create client + 2 past appointments via API")
    client = provision_paying_client(context, services)

    print("  Step 2: Create $30 entire-cart coupon via API")
    coupon_code = create_coupon_via_api(
        context, "Coupon entire cart - fixed amount", "fixed", "30"
    )

    cp_page, cp_context = open_portal(page, context, client["token"])
    try:
        print("  Step 3: Pay the past appointment_1 meeting with the coupon (mock gateway)")
        pay_meeting_with_coupon(cp_page, "appointment_1", coupon_code)

        print("  Step 4: Verify success page shows 'Payment confirmed' and $84.00")
        assert_payment_success(
            cp_page, title=CONFIRMED_TITLE, subtitle=CONFIRMED_SUBTITLE, amount=EXPECTED_AMOUNT
        )
        print("  [OK] cart fixed coupon -> $84.00")
    finally:
        cp_context.close()
