from playwright.sync_api import Page

from tests.payments.gateway_setups.payment_wizard_ui import (
    assert_mcc_dialog_present,
    currency_next_disabled,
    fill_preliminary_profession,
    open_payment_wizard,
)

PROFESSION = "Legal services"


def test_fill_profession(page: Page, context: dict) -> None:
    print("  Step 1: Open the payment onboarding wizard")
    open_payment_wizard(page)

    print("  Step 2: Verify the preliminary next button is disabled (no profession yet)")
    if not currency_next_disabled(page):
        raise AssertionError("Preliminary next button was expected to be disabled, but it was enabled")

    print(f"  Step 3: Fill the profession '{PROFESSION}'")
    fill_preliminary_profession(page, PROFESSION)

    print("  Step 4: Verify the MCC clarification dialog is shown")
    assert_mcc_dialog_present(page)
    print("  MCC dialog shown after filling the profession")
