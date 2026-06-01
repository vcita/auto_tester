from playwright.sync_api import Page

from tests.payments.offset_fees.offset_fees_account import prepare_account


def setup_convenience_fee_percentage(page: Page, context: dict) -> None:
    prepare_account(page, context)
