from playwright.sync_api import Page

from tests.products import products_helpers as ph

EXPECTED_TEMPLATE_NAME = "import_products"


def test_download_template(page: Page, context: dict) -> None:
    """Open the Import wizard and download the products import template."""
    page.set_default_timeout(ph.UI_TIMEOUT)

    print("  Step 1: Open the Import wizard")
    ph.open_import_wizard(page, context)

    print("  Step 2: Download the import template")
    filename = ph.download_template(page)
    print(f"  Downloaded: {filename}")
    assert EXPECTED_TEMPLATE_NAME in filename, (
        f"Expected downloaded file name to include {EXPECTED_TEMPLATE_NAME!r}, got {filename!r}"
    )

    print("  Step 3: Close the wizard")
    ph.close_wizard(page)
