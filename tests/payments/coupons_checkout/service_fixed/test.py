"""Apply a service fixed-amount coupon in the client-portal checkout.

Migrates automation-js features/salsa/coupons-pay.feature
(scenario: Client apply service fixed amount coupon in cp checkout).
"""

from playwright.sync_api import Page

from tests.payments.coupons_checkout.coupons_checkout_api import (
    create_coupon_via_api,
    provision_paying_client,
)
from tests.payments.coupons_checkout.coupons_checkout_cp import (
    assert_payment_success,
    close_balance_with_coupon,
    open_portal,
)

CONFIRMED_TITLE = "Payment confirmed"
CONFIRMED_SUBTITLE = "A confirmation email is on its way to your inbox"
EXPECTED_AMOUNT = "Amount received: $216.00"


def test_service_fixed(page: Page, context: dict) -> None:
    services = context["checkout_services"]

    print("  Step 1: Create client + 2 past appointments via API")
    client = provision_paying_client(context, services)

    print("  Step 2: Create a $20 coupon on the appointment_1 service via API")
    coupon_code = create_coupon_via_api(
        context,
        "Coupon on a service - fixed amount",
        "fixed",
        "20",
        valid_services=[services["appointment_1"]["id"]],
    )

    cp_page, cp_context = open_portal(page, context, client["token"])
    try:
        print("  Step 3: Close the whole balance from the payments list with the coupon (mock gateway)")
        close_balance_with_coupon(cp_page, coupon_code)

        print("  Step 4: Verify success page shows 'Payment confirmed' and $216.00")
        assert_payment_success(
            cp_page, title=CONFIRMED_TITLE, subtitle=CONFIRMED_SUBTITLE, amount=EXPECTED_AMOUNT
        )
        print("  [OK] service fixed coupon -> $216.00")
    finally:
        cp_context.close()
