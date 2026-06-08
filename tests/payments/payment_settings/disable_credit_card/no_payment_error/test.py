import time

from playwright.sync_api import Page

from tests.payments.payment_settings.payment_settings_api import set_allow_credit_card
from tests.payments.payment_settings.payment_settings_cp import submit_payment_and_expect_error
from tests.payments.payment_settings.payment_settings_ui import assert_provider_banner_displayed
from tests.payments.tips_settings.tips_gateway import connect_mock_gateway

PAY_AMOUNT = "100"


def test_no_payment_error(page: Page, context: dict) -> None:
    pay_for = f"service{int(time.time())}"

    print("  Step 1: Enter the payment settings page and assert the provider banner is displayed")
    assert_provider_banner_displayed(page, context)

    print("  Step 2: Connect the mock payment gateway (providers UI)")
    connect_mock_gateway(page, context)

    print("  Step 3: Disable credit-card payments via the API")
    set_allow_credit_card(context, False)

    print("  Step 4: As the client, open the make-payment form and verify the no-payment error")
    submit_payment_and_expect_error(
        page, context, pay_for=pay_for, amount=PAY_AMOUNT,
        email=context["cc_client_email"], first_name="first1",
    )
