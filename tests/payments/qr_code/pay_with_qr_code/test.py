"""Pay with QR code: grab the POS Pay-with-QR link, pay it in a second tab, confirm
the POS QR dialog success, and verify the back-office payment.

Migrates automation-js features/salsa/qr-code-payment.feature (scenario "pay with QR code").
"""

from playwright.sync_api import Page

from tests.payments.qr_code.qr_code_bo import assert_back_office_payment
from tests.payments.qr_code.qr_code_ui import (
    add_service_and_grab_qr_link,
    confirm_qr_dialog_success,
    open_pos_with_client,
    pay_link_in_new_tab,
)

EXPECTED_AMOUNT = "$100.00"
EXPECTED_TYPE = "Credit Card (Online)"


def test_pay_with_qr_code(page: Page, context: dict) -> None:
    service_name = context["qr_service_name"]

    print("  Step 1: Open the POS for the client...")
    open_pos_with_client(page, context)

    print(f"  Step 2: Add service '{service_name}' and grab the Pay-with-QR link...")
    link = add_service_and_grab_qr_link(page, context, service_name)
    print("    [OK] grabbed QR payment link")

    print("  Step 3: Pay the link in a second tab via the mock gateway...")
    pay_link_in_new_tab(page, link)
    print("    [OK] link paid, success page shown")

    print("  Step 4: Confirm the POS QR dialog shows payment success (realtime)...")
    confirm_qr_dialog_success(page)
    print("    [OK] QR dialog shows payment received")

    print("  Step 5: Verify the back-office payment...")
    assert_back_office_payment(page, context, service_name, EXPECTED_AMOUNT, EXPECTED_TYPE)
    print(
        f"    [OK] payment shows 'Payment for Sale #1 - {service_name}', "
        f"{EXPECTED_AMOUNT}, {EXPECTED_TYPE}, item '{service_name}'"
    )
