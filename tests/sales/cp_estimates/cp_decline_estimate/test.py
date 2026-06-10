# Auto-generated from script.md
# Source: tests/sales/cp_estimates/cp_decline_estimate/script.md
# Migrated from automation-js/features/steps/cp/estimates.feature (VCITA2-14024)

from playwright.sync_api import Page

from tests.sales.estimates import estimates_helpers as eh


def test_cp_decline_estimate(page: Page, context: dict) -> None:
    """
    A client declines a pending estimate in the client portal; the back-office
    estimate page reflects REJECTED.

    Prerequisites:
    - User logged in (Sales category _setup).
    """
    client = eh.create_client(context, first="Decline")
    estimate = eh.create_estimate_api(
        context,
        title="rejectEstimate",
        client_id=client["id"],
        items=[{
            "title": "product2",
            "amount": 10,
            "description": "description for payable item2",
            "quantity": 1,
        }],
    )
    print(f"  Created pending estimate {estimate['title']} for {client['name']}")

    print("  Step 1: Client opens the pending estimate in the client portal...")
    cp_page, cp_context = eh.open_cp_estimate_page(page, context, client["portal_token"])
    try:
        eh.assert_cp_estimate(
            cp_page,
            title=estimate["title"],
            price="10.00",
            client=client["name"],
            items=[{"name": "product2", "price": "10.00"}],
            status_actions=[r"Approve", r"Reject"],
        )

        print("  Step 2: Client declines the estimate...")
        eh.cp_perform_estimate_action(cp_page, "decline")
        eh.assert_cp_estimate_status(cp_page, "Declined on")
    finally:
        cp_context.close()

    print("  Step 3: Back-office estimate page shows REJECTED...")
    eh.open_bo_estimate(page, context, estimate["uid"])
    eh.assert_bo_estimate(
        page,
        title=estimate["title"],
        price="10.00",
        state="REJECTED",
        client=client["name"],
        total="10.00",
        items=[{"name": "product2", "description": "description for payable item2", "price": "10.00"}],
    )
