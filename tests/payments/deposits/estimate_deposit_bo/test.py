# Auto-generated from script.md
# Source: tests/payments/deposits/estimate_deposit_bo/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page

from tests.payments.deposits.deposits_estimate_ui import (
    approve_and_take_payment,
    assert_bo_estimate_deposit,
    create_estimate_with_deposit,
)


def test_estimate_deposit_bo(page: Page, context: dict) -> None:
    """Create an estimate with a $10 fixed deposit, verify SENT/DUE, then approve and take
    payment and verify APPROVED/PAID."""
    print("  Step 1: Create and send estimate with a $10 fixed deposit request")
    estimate_uid = create_estimate_with_deposit(
        page,
        context,
        title="bestimate",
        item_name="desired_item1",
        item_price="50",
        address="susa, persia",
        deposit_amount="10",
        can_client_pay=True,
    )

    print("  Step 2: Verify SENT with deposit DUE $10.00")
    assert_bo_estimate_deposit(
        page, context, estimate_uid, estimate_state="SENT", deposit_state="DUE", deposit_amount="$10.00"
    )

    print("  Step 3: Approve estimate and take payment (Cash)")
    approve_and_take_payment(page, context, estimate_uid)

    print("  Step 4: Verify APPROVED with deposit PAID $10.00")
    assert_bo_estimate_deposit(
        page, context, estimate_uid, estimate_state="APPROVED", deposit_state="PAID", deposit_amount="$10.00"
    )
    print("  [OK] Back-office estimate deposit verified")
