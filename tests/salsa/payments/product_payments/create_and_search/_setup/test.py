"""Setup for "Create and search product".

Mirrors the products.feature Background (client + $10 product) plus the
scenario's two-tax creation. The product under test ("product2") is created
through the UI in the test itself (the in-scope action).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.product_payments.product_payments_api import (
    seed_assign_taxes,
    seed_background,
)


def setup_create_search(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client first last + $10 product payable_item1 (API)")
    seed_background(
        context,
        first="first",
        last="last",
        email=f"test+{int(time.time() * 1000)}@vmeetme.com",
        product_name="payable_item1",
        price=10,
    )

    print("  Setup Step 3: Create two taxes 13% + 13.13% (API)")
    seed_assign_taxes(context)
    print("  [OK] setup complete - product payable_item1 + two taxes")
