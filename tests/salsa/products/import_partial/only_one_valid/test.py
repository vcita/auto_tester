import os

from playwright.sync_api import Page

from tests.salsa.products import products_helpers as ph

RESOURCES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources"
)
EXCEL_FILE = os.path.join(RESOURCES, "products_only_one_valid.xlsx")


def test_only_one_valid(page: Page, context: dict) -> None:
    """Import an Excel file with only one valid row; assert invalid rows are flagged
    in review and only the valid product (product 12) is imported."""
    page.set_default_timeout(ph.UI_TIMEOUT)

    print("  Steps 1-5: Import only-one-valid file (skip taxes), flag invalid rows, submit")
    ph.import_via_wizard(page, context, EXCEL_FILE, expect_invalid_rows=True)

    print("  Step 6: Reload products list to reflect the import")
    ph.open_products_page(page, context)

    print("  Step 7: Search 'product 12' -> ['product 12']")
    names = ph.search_products(page, "product 12", ["product 12"])
    assert names == ["product 12"], f"Expected ['product 12'], got {names}"
    print("  [OK] Only the valid product was imported")
