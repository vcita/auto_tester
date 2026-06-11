# Auto-generated from script.md
# Source: tests/sales/estimates/estimate_with_sections/script.md
# Migrated from automation-js/features/steps/estimates.feature (VCITA2-13789)

from playwright.sync_api import Page

import estimates_helpers as eh

BILLING_ADDRESS = "susa, persia"


def test_estimate_with_sections(page: Page, context: dict) -> None:
    """
    Create an estimate with a top-level item plus a section grouping a second item.

    Top level: service ($100). Section "section1" contains product2 ($10).
    Estimate total = $110.00; section total = $10.00.
    """
    eh.set_tax_mode(context, "exclude")
    client = eh.create_client(context)
    service = context["sales_service_name"]
    product = context["sales_product_name"]
    product_desc = context["sales_product_description"]

    print("  Step 1: Create estimate with a top-level item and a section...")
    billing, wizard = eh.open_new_estimate(page, client["name"])
    eh.set_title(wizard, "bestimate")
    eh.add_existing_item(wizard, service)
    eh.add_section(wizard, "section1")
    eh.add_existing_item(wizard, product)
    eh.set_billing_address(wizard, BILLING_ADDRESS)
    eh.send_estimate(wizard)
    page.wait_for_timeout(3000)

    estimate = eh.latest_estimate_for_client(context, client["id"])
    print(f"    created {estimate['title']}")

    print("  Step 2: Back-office page displays top-level item and section...")
    eh.open_bo_estimate(page, context, estimate["uid"])
    eh.assert_bo_estimate(
        page,
        title=estimate["title"],
        price="110.00",
        state="SENT",
        client=client["name"],
        total="110.00",
        items=[{"name": service, "price": "100.00"}],
    )
    eh.assert_bo_section(
        page,
        section_name="section1",
        section_total="$10.00",
        section_item={"name": product, "description": product_desc},
    )

    context["sections_estimate_title"] = estimate["title"]
