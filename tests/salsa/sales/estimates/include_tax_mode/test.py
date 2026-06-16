# Auto-generated from script.md
# Source: tests/sales/estimates/include_tax_mode/script.md
# Migrated from automation-js/features/steps/estimates.feature (VCITA2-13789)

from playwright.sync_api import Page

import estimates_helpers as eh

BILLING_ADDRESS = "susa, persia"


def test_include_tax_mode(page: Page, context: dict) -> None:
    """
    With tax_mode=include, custom taxed items must produce a tax-inclusive total.

    desired_item1 ($50, tax 13%, included) + desired_item2 ($20) => total $70.00
    (vs $76.50 in the default exclude mode).
    """
    eh.set_tax_mode(context, "include")
    client = eh.create_client(context)

    print("  Step 1: Create estimate with custom taxed items (tax_mode=include)...")
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

    estimate = eh.latest_estimate_for_client(context, client["id"])
    print(f"    created {estimate['title']}")

    print("  Step 2: Back-office total is tax-inclusive ($70.00)...")
    eh.open_bo_estimate(page, context, estimate["uid"])
    eh.assert_bo_estimate(
        page,
        title=estimate["title"],
        price="70.00",
        state="SENT",
        client=client["name"],
        total="70.00",
        items=[
            {"name": "desired_item1", "description": "long long description", "price": "50.00"},
            {"name": "desired_item2", "description": "short desc", "price": "20.00"},
        ],
    )

    context["include_mode_estimate_title"] = estimate["title"]
