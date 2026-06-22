# Source: tests/payments/qr_code_payment/pay_with_qr/script.md
# Migrated from automation-js/features/salsa/qr-code-payment.feature (VCITA2-13850)

from playwright.sync_api import Page

from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway
from tests.salsa.payments.qr_code_payment.qr_code_payment_helpers import (
    assert_payment_page,
    assert_qr_dialog_success,
    grab_qr_link,
    pay_via_link,
)

EXPECTED_AMOUNT = "$100.00"
EXPECTED_TYPE = "Credit Card (Online)"


def test_pay_with_qr(page: Page, context: dict) -> None:
    """Grab a QR payment link from the POS for the paid service, pay it via the
    client-portal link in a separate tab through the mock gateway, verify the QR
    dialog success, then verify the back-office payment page."""
    client_name = context["qr_client_name"]
    client_first = context["qr_client_first_name"]
    service_name = context["qr_service_name"]
    payment_name = f"Payment for Sale #1 - {service_name}"

    print("  Step 1: Connect the mock payment gateway (back office)")
    connect_mock_gateway(page, context)

    print(f"  Step 2: Grab a QR payment link from the POS ({service_name}, $100)")
    link = grab_qr_link(page, context, service_name=service_name, client_name=client_name)

    print("  Step 3: Pay the link in a separate tab via the mock gateway")
    pay_via_link(page, link)

    print("  Step 4: Verify the back-office QR dialog shows payment success")
    assert_qr_dialog_success(page)

    print("  Step 5: Verify the Payments Received payment page")
    assert_payment_page(
        page,
        search_term=client_first,
        name=payment_name,
        amount=EXPECTED_AMOUNT,
        payment_type=EXPECTED_TYPE,
        items=[service_name],
    )
    print("  [OK] QR code payment verified")
