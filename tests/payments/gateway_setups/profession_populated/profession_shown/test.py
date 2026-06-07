from playwright.sync_api import Page

from tests.payments.gateway_setups.payment_wizard_ui import (
    open_payment_wizard,
    read_preliminary_profession,
)

EXPECTED_PROFESSION = "Legal services"


def test_profession_shown(page: Page, context: dict) -> None:
    print("  Step 1: Open the payment onboarding wizard")
    open_payment_wizard(page)

    print("  Step 2: Read the prepopulated preliminary profession")
    profession = read_preliminary_profession(page)
    if profession != EXPECTED_PROFESSION:
        raise AssertionError(
            f"Preliminary profession: expected '{EXPECTED_PROFESSION}', got '{profession}'"
        )
    print(f"  Profession prepopulated with '{profession}'")
