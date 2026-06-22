from playwright.sync_api import Page

from tests.salsa.payments.invoices.invoice_billing_setup import seed_invoice_account


def setup_invoice_items_copy(page: Page, context: dict) -> None:
    seed_invoice_account(page, context, with_tax=True)
