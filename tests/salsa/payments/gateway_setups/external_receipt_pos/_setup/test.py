"""Setup for the external-receipt POS scenario.

Log in (point_of_sale stays enabled), create the 'simon bolivar' client, and assign the
mockreceipts external-receipt app.
"""

from playwright.sync_api import Page

from tests.salsa.payments.gateway_setups.gateway_setups_account import prepare_receipt_account


def setup_external_receipt_pos(page: Page, context: dict) -> None:
    prepare_receipt_account(page, context, deny_pos=False)
