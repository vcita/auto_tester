from playwright.sync_api import Page

from tests.products.products_account import (
    IMPORT_PRODUCTS_FLAG,
    enable_features,
    login,
)


def setup_partial_import(page: Page, context: dict) -> None:
    print("  Step: Enable import_products feature flag (before login)")
    enable_features(context, IMPORT_PRODUCTS_FLAG)
    print("  Step: Log in to isolated account")
    login(page, context)
    print("  Setup complete - import_products enabled, logged in")
