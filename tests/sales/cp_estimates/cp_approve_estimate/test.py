# Auto-generated from script.md
# Source: tests/sales/cp_estimates/cp_approve_estimate/script.md
# Migrated from automation-js/features/steps/cp/estimates.feature (VCITA2-14024)

from playwright.sync_api import Page

from tests.sales.estimates import estimates_helpers as eh


def test_cp_approve_estimate(page: Page, context: dict) -> None:
    """
    A client approves a pending estimate in the client portal; the back-office
    estimate page reflects APPROVED.

    Prerequisites:
    - User logged in (Sales category _setup).
    """
    client = eh.create_client(context, first="Approve")
    estimate = eh.create_estimate_api(
        context,
        title="approveEstimate",
        client_id=client["id"],
        items=[
            {"title": "service", "amount": 100, "description": "", "quantity": 1},
            {"title": "product_item200", "amount": 20, "description": "short desc", "quantity": 1},
        ],
    )
    print(f"  Created pending estimate {estimate['title']} (total 120.00) for {client['name']}")

    print("  Step 1: Client opens the pending estimate in the client portal...")
    cp_page, cp_context = eh.open_cp_estimate_page(page, context, client["portal_token"])
    try:
        eh.assert_cp_estimate(
            cp_page,
            title=estimate["title"],
            price="120.00",
            client=client["name"],
            items=[
                {"name": "service", "price": "100.00"},
                {"name": "product_item200", "price": "20.00"},
            ],
            status_actions=[r"Approve", r"Reject"],
        )

        print("  Step 2: Client approves the estimate...")
        eh.cp_perform_estimate_action(cp_page, "approve")
        eh.assert_cp_estimate_status(cp_page, "Approved on")
    finally:
        cp_context.close()

    print("  Step 3: Back-office estimate page shows APPROVED...")
    eh.open_bo_estimate(page, context, estimate["uid"])
    eh.assert_bo_estimate(
        page,
        title=estimate["title"],
        price="120.00",
        state="APPROVED",
        client=client["name"],
        total="120.00",
        items=[
            {"name": "service", "price": "100.00"},
            {"name": "product_item200", "description": "short desc", "price": "20.00"},
        ],
    )
