from playwright.sync_api import Page

from tests.salsa.payments.refunds_credits.partial_refund_account import prepare_account


def setup_partial_refund_bo(page: Page, context: dict) -> None:
    prepare_account(page, context, deny_pos=True)
