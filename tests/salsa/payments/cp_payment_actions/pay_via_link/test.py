"""Client pays a $100 service via the CP pay link, then it appears in BO search.

Migrates automation-js features/salsa/cp/payment-actions.feature
(Scenario: "Client payment action in CP via link").
"""

import time

from playwright.sync_api import Page

from tests.salsa.payments.cp_payment_actions.cp_payment_actions_helpers import (
    assert_payment_in_search,
    pay_via_payment_form,
)


def test_pay_via_link(page: Page, context: dict) -> None:
    store = context["cp_payment_actions"]
    service_name = store["service"]["name"]

    print("  Step 1: New client 'steve' pays the $100 service via the public pay link")
    pay_via_payment_form(
        page, context,
        pay_for=service_name, amount="100",
        first_name="steve", email=f"test3+{int(time.time() * 1000)}@vmeetme.com",
    )

    print("  Step 2: Assert the payment appears in BO Payments Received (search 'steve')")
    assert_payment_in_search(
        page, first_name="steve", expected_substrings=["Payment for", service_name]
    )
    print("  [OK] pay-via-link payment found in back office")
