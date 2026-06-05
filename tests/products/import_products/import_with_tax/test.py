import os

from playwright.sync_api import Page

from tests.products import products_helpers as ph

RESOURCES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources"
)
EXCEL_FILE = os.path.join(RESOURCES, "products_with_sku.xlsx")


def test_import_with_tax(page: Page, context: dict) -> None:
    """Import 3 products from Excel with a tax assigned, then verify search and tax.

    Reads from context (set by _setup): import_tax_name, import_tax_rate.
    """
    page.set_default_timeout(ph.UI_TIMEOUT)
    tax_name = context["import_tax_name"]
    tax_rate = context["import_tax_rate"]

    print("  Step 1: Open the Import wizard")
    ph.open_import_wizard(page, context)

    print("  Step 2: Upload products_with_sku.xlsx (3 products)")
    ph.upload_file(page, EXCEL_FILE)

    print(f"  Step 3: Assign tax {tax_name} ({tax_rate}%) during import")
    ph.select_tax(page, tax_name, tax_rate)

    print("  Step 4: Import and confirm success")
    ph.submit_import(page)

    print("  Step 5: Reload products list to reflect the import")
    ph.open_products_page(page, context)

    print("  Step 6: Search by name 'product 11' -> ['product 11']")
    names = ph.search_products(page, "product 11", ["product 11"])
    assert names == ["product 11"], f"Expected ['product 11'], got {names}"

    print("  Step 7: Search by SKU 'sku12' -> ['product 12']")
    names = ph.search_products(page, "sku12", ["product 12"])
    assert names == ["product 12"], f"Expected ['product 12'], got {names}"

    print("  Step 8: Verify product 12 tax")
    expected_tax = f"{tax_name} ({tax_rate}%)"
    actual_tax = ph.get_product_tax(page, "product 12")
    assert actual_tax == expected_tax, f"Expected tax {expected_tax!r}, got {actual_tax!r}"
    print(f"  [OK] product 12 tax is {actual_tax!r}")
