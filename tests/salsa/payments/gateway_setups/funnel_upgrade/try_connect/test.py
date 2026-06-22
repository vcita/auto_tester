from playwright.sync_api import Page

from tests.salsa.payments.gateway_setups.payment_wizard_ui import (
    assert_wizard_dialog_present,
    open_payment_wizard,
    try_connect_gateway,
)


def test_try_connect(page: Page, context: dict) -> None:
    print("  Step 1: Open the payment onboarding wizard")
    open_payment_wizard(page)

    print("  Step 2: Try to connect a third-party (Stripe) gateway")
    try_connect_gateway(page)

    print("  Step 3: Verify the upgrade dialog is shown (funnel v1 requires upgrade)")
    assert_wizard_dialog_present(page, label="Upgrade")
    print("  Upgrade dialog shown")
