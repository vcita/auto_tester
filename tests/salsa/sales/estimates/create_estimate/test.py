# Auto-generated from script.md
# Source: tests/sales/estimates/create_estimate/script.md
# Migrated from automation-js/features/steps/estimates.feature (VCITA2-13789)

from playwright.sync_api import Page

import estimates_helpers as eh

BILLING_ADDRESS = "susa, persia"


def test_create_estimate(page: Page, context: dict) -> None:
    """
    Business creates estimates and verifies search, back-office and client-portal views.

    Prerequisites:
    - User logged in (category _setup), shared service/product/tax created.

    Saves to context: created_estimate_one_title, created_estimate_two_title.
    """
    eh.set_tax_mode(context, "exclude")
    client = eh.create_client(context)
    service = context["sales_service_name"]
    product = context["sales_product_name"]
    product_desc = context["sales_product_description"]

    print("  Step 1: Create first estimate (existing items, reordered)...")
    billing, wizard = eh.open_new_estimate(page, client["name"])
    eh.set_title(wizard, "bestimate")
    eh.add_existing_item(wizard, service)
    eh.add_existing_item(wizard, product)
    eh.set_billing_address(wizard, BILLING_ADDRESS)
    eh.reorder_first_two_items(page, wizard)
    eh.send_estimate(wizard)
    page.wait_for_timeout(3000)

    estimate_one = eh.latest_estimate_for_client(context, client["id"])
    print(f"    created {estimate_one['title']}")

    print("  Step 2: Search returns the first estimate...")
    results = eh.search_estimates_by_client(page, client["name"])
    if results != [estimate_one["title"]]:
        raise AssertionError(f"Expected [{estimate_one['title']}], got {results}")

    print("  Step 3: Back-office page displays the first estimate...")
    eh.open_bo_estimate(page, context, estimate_one["uid"])
    eh.assert_bo_estimate(
        page,
        title=estimate_one["title"],
        price="110.00",
        state="SENT",
        client=client["name"],
        total="110.00",
        items=[
            {"name": product, "description": product_desc, "price": "10.00"},
            {"name": service, "price": "100.00"},
        ],
        ordered_names=[product, service],
    )

    print("  Step 4: Create second estimate (custom taxed items)...")
    billing, wizard = eh.open_new_estimate(page, client["name"])
    eh.set_title(wizard, "bestimate")
    eh.add_custom_item(
        wizard, "desired_item1", "50", description="long long description",
        tax_name=context["sales_tax_name"], save_item=False,
    )
    eh.add_custom_item(
        wizard, "desired_item2", "20", description="short desc", save_item=True,
    )
    eh.set_billing_address(wizard, BILLING_ADDRESS)
    eh.send_estimate(wizard)
    page.wait_for_timeout(3000)

    estimate_two = eh.latest_estimate_for_client(context, client["id"])
    print(f"    created {estimate_two['title']}")

    print("  Step 5: Search returns both estimates, newest first...")
    results = eh.search_estimates_by_client(page, client["name"])
    if results != [estimate_two["title"], estimate_one["title"]]:
        raise AssertionError(
            f"Expected [{estimate_two['title']}, {estimate_one['title']}], got {results}"
        )

    print("  Step 6: Back-office page displays the second estimate (tax excluded = 76.50)...")
    eh.open_bo_estimate(page, context, estimate_two["uid"])
    eh.assert_bo_estimate(
        page,
        title=estimate_two["title"],
        price="76.50",
        state="SENT",
        client=client["name"],
        total="76.50",
        items=[
            {"name": "desired_item1", "description": "long long description", "price": "50.00"},
            {"name": "desired_item2", "description": "short desc", "price": "20.00"},
        ],
    )

    print("  Step 7: Client portal displays the first (pending) estimate...")
    cp_page, cp_context = eh.open_cp_estimate_page(page, context, client["portal_token"])
    try:
        eh.assert_cp_estimate(
            cp_page,
            title=estimate_one["title"],
            price="110.00",
            client=client["name"],
            items=[
                {"name": product, "price": "10.00"},
                {"name": service, "price": "100.00"},
            ],
            status_actions=[r"Approve", r"Accept"],
        )
    finally:
        cp_context.close()

    context["created_estimate_one_title"] = estimate_one["title"]
    context["created_estimate_two_title"] = estimate_two["title"]
