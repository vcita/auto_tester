"""Setup for the "edit and cancel product's payment request" scenario.

Mirrors the products.feature Background plus the scenario's "assigns a product to
client via API" Given.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.product_payments.product_payments_api import (
    assign_product_via_api,
    seed_background,
)


def setup_edit_cancel(page: Page, context: dict) -> None:
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

    print("  Setup Step 3: Assign payable_item1 to first last (API)")
    assign_product_via_api(context, product_name="payable_item1")
    print("  [OK] setup complete - product order DUE for 'first last'")
