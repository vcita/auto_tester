from playwright.sync_api import Page

from tests.payments.refunds_credits.partial_refund_account import prepare_account


def setup_partial_refund_pos(page: Page, context: dict) -> None:
    prepare_account(page, context, deny_pos=False)
