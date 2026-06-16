"""Apply a service percentage coupon (created in the UI) in the client-portal checkout.

Migrates automation-js features/salsa/coupons-pay.feature
(scenario: Client apply service percentage coupon in cp checkout). The coupon is created
through the Settings/Coupons UI (not the API) to exercise the UI creation path.
"""

from playwright.sync_api import Page

from tests.salsa.payments.coupons_checkout.coupons_checkout_api import provision_paying_client
from tests.salsa.payments.coupons_checkout.coupons_checkout_cp import (
    assert_payment_success,
    close_balance_with_coupon,
    create_service_coupon_ui,
    open_portal,
)

CONFIRMED_TITLE = "Payment confirmed"
CONFIRMED_SUBTITLE = "A confirmation email is on its way to your inbox"
EXPECTED_AMOUNT = "Amount received: $228.00"


def test_service_percentage_ui(page: Page, context: dict) -> None:
    services = context["checkout_services"]

    print("  Step 1: Create client + 2 past appointments via API")
    client = provision_paying_client(context, services)

    print("  Step 2: Create a 10% coupon on the appointment_1 service via the UI")
    coupon_code = create_service_coupon_ui(
        page, "Percentage", "Coupon on a service - percentage", "10", "appointment_1"
    )

    cp_page, cp_context = open_portal(page, context, client["token"])
    try:
        print("  Step 3: Close the whole balance from the payments list with the coupon (mock gateway)")
        close_balance_with_coupon(cp_page, coupon_code)

        print("  Step 4: Verify success page shows 'Payment confirmed' and $228.00")
        assert_payment_success(
            cp_page, title=CONFIRMED_TITLE, subtitle=CONFIRMED_SUBTITLE, amount=EXPECTED_AMOUNT
        )
        print("  [OK] service percentage coupon (UI) -> $228.00")
    finally:
        cp_context.close()
