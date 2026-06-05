"""Account preparation helpers for the import_products subcategories.

Handles the ``import_products`` feature flag (enabled before login), login to the
isolated account, and tax creation via the same endpoint the product UI uses.
Feature-flag and token helpers live in :mod:`tests.account_api`.
"""

import requests
from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import (  # re-exported for subcategory setups
    REQUEST_TIMEOUT,
    account_token,
    api_base,
    enable_features,
)

__all__ = [
    "IMPORT_PRODUCTS_FLAG",
    "enable_features",
    "login",
    "create_tax_via_api",
]

IMPORT_PRODUCTS_FLAG = "import_products"
TAXES_PATH = "/business/payments/v1/taxes"


def login(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")
    fn_login(page, context, username=username, password=password)


def create_tax_via_api(context: dict, name: str, rate: int) -> dict:
    """Create a tax through ``POST business/payments/v1/taxes`` (the endpoint the
    products tax flow uses) and return the created tax object."""
    response = requests.post(
        f"{api_base(context)}{TAXES_PATH}",
        json={"tax": {"name": name, "rate": rate, "default_for_categories": []}, "new_api": True},
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["data"]["tax"]
