# Source: tests/payments/appointment_payments/packaged_service/packaged_service/script.md
# Migrated from automation-js/features/salsa/appointment-payments.feature (VCITA2-13857)

from playwright.sync_api import Page

from tests.salsa.payments.appointment_payments.appointment_payments_helpers import (
    assert_appt_payment_request,
    cancel_package_redemption,
    mark_appt_completed,
    redeem_appt_with_package,
)


def test_packaged_service(page: Page, context: dict) -> None:
    """meeting1 completed -> DUE $100; meeting2 redeemed with package -> PAID $0;
    cancel meeting2 redemption -> DUE $100 with the credit refunded."""
    print("  Step 1: Mark meeting1 completed -> DUE $100.00")
    mark_appt_completed(page, context, identifier="meeting1")
    assert_appt_payment_request(page, context, {
        "state": "DUE", "amount": "$100.00",
    }, identifier="meeting1")

    print("  Step 2: Redeem meeting2 with the package -> PAID $0.00 (redeemed)")
    mark_appt_completed(page, context, identifier="meeting2")
    redeem_appt_with_package(page, context, identifier="meeting2")
    assert_appt_payment_request(page, context, {
        "state": "PAID", "amount": "$0.00",
        "redeemed_with_package": "true", "package_name": "package",
    }, identifier="meeting2")

    print("  Step 3: Cancel meeting2 package redemption -> DUE $100.00 (credit refunded)")
    cancel_package_redemption(page, context, identifier="meeting2")
    assert_appt_payment_request(page, context, {
        "state": "DUE", "amount": "$100.00",
        "package_credit_refunded": "true", "package_name": "package",
    }, identifier="meeting2")

    print("  [OK] packaged-service appointment redemption + refund verified")
