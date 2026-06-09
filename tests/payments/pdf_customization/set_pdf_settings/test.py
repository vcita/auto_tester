"""Set PDF customization template, logo size, and brand color type, then verify persistence.

Migrates automation-js features/steps/payments-settings/pdf-customization.feature
(scenario: set template, logo size, and brand color type).
"""

from playwright.sync_api import Page

from tests.payments.pdf_customization.pdf_customization_helpers import (
    open_pdf_customization,
    read_pdf_settings,
    save_settings,
    set_brand_color_type,
    set_logo_size,
    set_template,
)

TEMPLATE = "modern"
LOGO_SIZE = "Small"
BRAND_COLOR_TYPE = "custom"
EXPECTED_BRAND_COLOR = "#000000"


def test_set_pdf_settings(page: Page, context: dict) -> None:
    print("  Step 1: Open PDF customization settings...")
    open_pdf_customization(page)

    print(f"  Step 2: Set template '{TEMPLATE}', logo size '{LOGO_SIZE}', brand color '{BRAND_COLOR_TYPE}'...")
    set_template(page, TEMPLATE)
    set_logo_size(page, LOGO_SIZE)
    set_brand_color_type(page, BRAND_COLOR_TYPE)

    print("  Step 3: Save settings...")
    save_settings(page)

    print("  Step 4: Reload and read back the persisted settings...")
    actual = read_pdf_settings(page)

    expected = {
        "template": TEMPLATE,
        "logo_size": LOGO_SIZE,
        "brand_color_type": BRAND_COLOR_TYPE,
        "brand_color": EXPECTED_BRAND_COLOR,
    }
    if actual != expected:
        raise AssertionError(f"PDF customization settings: expected {expected}, got {actual}")

    context["pdf_customization"] = actual
    print("  [OK] PDF customization template/logo-size/brand-color persisted")
