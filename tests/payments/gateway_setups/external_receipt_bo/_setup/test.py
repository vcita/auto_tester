"""Setup for the external-receipt back-office scenario.

Deny point_of_sale (so Quick Actions exposes the legacy Record payment dialog), log in,
create the 'simon bolivar' client, and assign the mockreceipts external-receipt app.
"""

from playwright.sync_api import Page

from tests.payments.gateway_setups.gateway_setups_account import prepare_receipt_account


def setup_external_receipt_bo(page: Page, context: dict) -> None:
    prepare_receipt_account(page, context, deny_pos=True)
