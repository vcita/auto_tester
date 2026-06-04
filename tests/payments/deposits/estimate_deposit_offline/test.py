# Auto-generated from script.md
# Source: tests/payments/deposits/estimate_deposit_offline/script.md

from playwright.sync_api import Page

from tests.payments.deposits.deposits_api import (
    create_deposit_request,
    create_estimate_via_api,
    create_product,
)
from tests.payments.deposits.deposits_cp_ui import (
    approve_offline,
    assert_cp_deposit,
    assert_offline_deposit_page,
    goto_estimates_list,
    open_estimate,
    open_portal,
)
from tests.sales.estimates.estimates_helpers import latest_estimate_for_client


def test_estimate_deposit_offline(page: Page, context: dict) -> None:
    """Client approves an estimate whose $10 deposit cannot be paid online; the client is sent
    to the offline-deposit page and the estimate is approved with the deposit OFFLINE."""
    token = context["deposit_client_token"]
    client = context["deposit_client"]

    # No mock-gateway connect here: an offline deposit (can_client_pay=false) is never paid
    # online, and the shared account already has the gateway connected from the prior CP scenario.
    print("  Step 1: Create estimate + $10 offline deposit via API")
    product = create_product(context, "product21", "80", "description for payable item21")
    estimate = create_estimate_via_api(context, "bestimate_offline", client, [product], send_email=True)
    create_deposit_request(context, estimate, amount="10", total="10", can_client_pay=False)
    title = latest_estimate_for_client(context, client["id"])["title"]

    cp_page, cp_context = open_portal(page, context, token)
    try:
        print("  Step 2: Verify pending estimate shows deposit DUE $10.00 (offline only)")
        open_estimate(cp_page, title)
        assert_cp_deposit(cp_page, deposit_state="DUE", deposit_amount="$10.00", can_client_pay=False)

        print("  Step 3: Approve the estimate")
        approve_offline(cp_page)

        print("  Step 4: Verify redirect to the offline deposit page ($10.00)")
        assert_offline_deposit_page(cp_page, "$10.00")

        print("  Step 5: Re-open the approved estimate and verify deposit OFFLINE")
        goto_estimates_list(cp_page, context, token, done_tab=True)
        open_estimate(cp_page, title)
        assert_cp_deposit(cp_page, deposit_state="OFFLINE", deposit_amount="$10.00")
        print("  [OK] CP offline deposit approval verified")
    finally:
        cp_context.close()
