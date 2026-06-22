"""Setup for "payments request created for product in mode include".

Mirrors the products.feature Background plus the scenario's "denies point_of_sale",
two-tax creation, and "tax_mode = include" so taxes are included in the price.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import deny_features
from tests.salsa.payments.product_payments.product_payments_api import (
    seed_assign_taxes,
    seed_background,
    set_tax_mode,
)


def setup_request_include(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Deny point_of_sale")
    deny_features(context, "point_of_sale")

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Seed client first last + $10 product payable_item1 (API)")
    seed_background(
        context,
        first="first",
        last="last",
        email=f"test+{int(time.time() * 1000)}@vmeetme.com",
        product_name="payable_item1",
        price=10,
    )

    print("  Setup Step 4: Create two taxes 13% + 13.13% (API)")
    seed_assign_taxes(context)

    print("  Setup Step 5: Set tax_mode = include (API)")
    set_tax_mode(context, "include")
    print("  [OK] setup complete - product + two taxes (include mode) for 'first last'")
