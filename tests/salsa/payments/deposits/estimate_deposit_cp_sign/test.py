# Auto-generated from script.md
# Source: tests/payments/deposits/estimate_deposit_cp_sign/script.md

from playwright.sync_api import Page

from tests.salsa.payments.deposits.deposits_api import (
    create_deposit_request,
    create_estimate_via_api,
    create_product,
)
from tests.salsa.payments.deposits.deposits_cp_ui import (
    assert_cp_deposit,
    assert_payment_success,
    goto_estimates_list,
    open_estimate,
    open_portal,
    sign_and_pay_deposit,
)
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway
from tests.salsa.sales.estimates.estimates_helpers import latest_estimate_for_client


def test_estimate_deposit_cp_sign(page: Page, context: dict) -> None:
    """Client signs and pays an estimate's $10 deposit in the portal via the mock gateway,
    then the estimate is approved with the deposit PAID."""
    token = context["deposit_client_token"]
    client = context["deposit_client"]

    print("  Step 1: Connect mock gateway and create estimate + $10 deposit via API")
    connect_mock_gateway(page, context)
    product = create_product(context, "product21", "80", "description for payable item21")
    estimate = create_estimate_via_api(
        context, "bestimate_sign", client, [product], send_email=True, is_signature_required=True
    )
    create_deposit_request(context, estimate, amount="10", total="10", can_client_pay=True)
    title = latest_estimate_for_client(context, client["id"])["title"]

    cp_page, cp_context = open_portal(page, context, token)
    try:
        print("  Step 2: Verify pending estimate shows deposit DUE $10.00")
        open_estimate(cp_page, title)
        assert_cp_deposit(cp_page, deposit_state="DUE", deposit_amount="$10.00", can_client_pay=True)

        print("  Step 3: Sign and pay the deposit via the mock gateway")
        sign_and_pay_deposit(cp_page)

        print("  Step 4: Verify payment success page shows $10.00")
        assert_payment_success(cp_page, "$10.00")

        print("  Step 5: Re-open the approved estimate and verify deposit PAID $10.00")
        goto_estimates_list(cp_page, context, token, done_tab=True)
        open_estimate(cp_page, title)
        assert_cp_deposit(cp_page, deposit_state="PAID", deposit_amount="$10.00")
        print("  [OK] CP sign + pay deposit verified")
    finally:
        cp_context.close()
