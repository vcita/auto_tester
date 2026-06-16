from playwright.sync_api import Page

from tests.salsa.payments.offset_fees.offset_fees_account import prepare_account


def setup_surcharge(page: Page, context: dict) -> None:
    prepare_account(page, context)
