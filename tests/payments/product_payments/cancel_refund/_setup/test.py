"""Setup for the "Cancel and refund paid product" scenario (isolated account).

Mirrors the products.feature Background plus the scenario's "denies feature flags:
point_of_sale" and "assigns a product to client via API" Given.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import deny_features
from tests.payments.product_payments.product_payments_api import (
    assign_product_via_api,
    seed_background,
)


def setup_cancel_refund(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Deny point_of_sale (record-payment, not POS)")
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

    print("  Setup Step 4: Assign payable_item1 to first last (API)")
    assign_product_via_api(context, product_name="payable_item1")
    print("  [OK] setup complete - product order DUE for 'first last'")
