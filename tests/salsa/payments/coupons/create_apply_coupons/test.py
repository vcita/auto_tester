"""Create and apply coupons of types fixed & percentage.

Migrates automation-js features/salsa/coupons.feature
(scenario: Create and apply coupons of types fixed & percentage).
"""

from playwright.sync_api import Page

from tests.salsa.payments.coupons.coupons_helpers import (
    apply_coupon,
    assert_coupons,
    assert_payment_request,
    create_coupon,
    open_appointment,
    open_coupons_settings,
)

# (coupon_type, coupon_name, amount, expected_discount_label)
COUPONS = [
    ("Fixed amount", "20 off coupon", "20", "$20 off"),
    ("Percentage", "10% coupon", "10", "10% off"),
    ("Percentage", "100% coupon", "100", "100% off"),
]

# alias -> (coupon_name, expected_state, expected_balance)
APPLICATIONS = {
    "appointment_1": ("20 off coupon", "NOT YET DUE", "$80.00"),
    "appointment_2": ("10% coupon", "NOT YET DUE", "$90.00"),
    "appointment_3": ("100% coupon", "PAID", "$0.00"),
}


def test_create_apply_coupons(page: Page, context: dict) -> None:
    base_url = context["base_url"]
    bookings = context["coupon_bookings"]

    print("  Step 1: Open Coupons settings...")
    scope = open_coupons_settings(page)

    print("  Step 2: Create fixed and percentage coupons...")
    for coupon_type, name, amount, _ in COUPONS:
        create_coupon(page, scope, coupon_type, name, amount)

    print("  Step 3: Verify the coupons list shows the expected discounts...")
    assert_coupons(page, {name: discount for _, name, _, discount in COUPONS})

    print("  Step 4: Apply each coupon and verify the appointment payment request...")
    for alias, (coupon_name, state, balance) in APPLICATIONS.items():
        appointment_scope = open_appointment(page, base_url, bookings[alias])
        apply_coupon(page, appointment_scope, coupon_name)
        assert_payment_request(page, state, balance)
        print(f"    [OK] {alias}: {coupon_name} -> {state} {balance}")

    print("  [OK] Coupons created, listed, applied, and payment requests verified")
