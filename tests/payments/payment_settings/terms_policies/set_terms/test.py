from playwright.sync_api import Page

from tests.payments.payment_settings.payment_settings_api import (
    get_terms_and_policies,
    set_terms_and_policies,
)
from tests.payments.payment_settings.payment_settings_ui import read_terms_text

TERMS_TEXT = "terms and policies example"


def test_set_terms(page: Page, context: dict) -> None:
    print(f"  Step 1: Set custom terms & policies text via API: '{TERMS_TEXT}'")
    set_terms_and_policies(context, TERMS_TEXT)

    print("  Step 2: Assert the API read-back persisted the text")
    persisted = get_terms_and_policies(context)
    if persisted != TERMS_TEXT:
        raise AssertionError(f"terms read-back: expected '{TERMS_TEXT}', got '{persisted}'")

    print("  Step 3: Assert the terms-and-policies settings tab displays the text")
    displayed = read_terms_text(page, context)
    if displayed != TERMS_TEXT:
        raise AssertionError(f"terms displayed: expected '{TERMS_TEXT}', got '{displayed}'")
