from playwright.sync_api import Page

from tests.products.products_account import (
    IMPORT_PRODUCTS_FLAG,
    create_tax_via_api,
    enable_features,
    login,
)

TAX_NAME = "ImportTax"
TAX_RATE = 13


def setup_excel_import(page: Page, context: dict) -> None:
    print("  Step: Enable import_products feature flag (before login)")
    enable_features(context, IMPORT_PRODUCTS_FLAG)
    print(f"  Step: Create tax {TAX_NAME} ({TAX_RATE}%) via API")
    create_tax_via_api(context, TAX_NAME, TAX_RATE)
    context["import_tax_name"] = TAX_NAME
    context["import_tax_rate"] = TAX_RATE
    print("  Step: Log in to isolated account")
    login(page, context)
    print("  Setup complete - import_products enabled, tax created, logged in")
