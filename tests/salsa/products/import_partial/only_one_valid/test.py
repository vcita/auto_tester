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

    print("  Step 1: Open the Import wizard")
    ph.open_import_wizard(page, context)

    print("  Step 2: Upload products_only_one_valid.xlsx (1 of 3 valid)")
    ph.upload_file(page, EXCEL_FILE)

    print("  Step 3: Skip taxes -> review step")
    ph.skip_taxes(page)

    print("  Step 4: Assert invalid rows are flagged in review")
    error_count = ph.assert_error_rows_present(page)
    print(f"  [OK] {error_count} invalid row(s) flagged")

    print("  Step 5: Import and confirm success")
    ph.submit_import(page)

    print("  Step 6: Reload products list to reflect the import")
    ph.open_products_page(page, context)

    print("  Step 7: Search 'product 12' -> ['product 12']")
    names = ph.search_products(page, "product 12", ["product 12"])
    assert names == ["product 12"], f"Expected ['product 12'], got {names}"
    print("  [OK] Only the valid product was imported")
