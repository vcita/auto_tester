from playwright.sync_api import Page

from tests.payments.invoices.invoice_billing_api import set_late_fee_settings
from tests.payments.invoices.invoice_billing_setup import seed_invoice_account


def setup_invoice_late_fee(page: Page, context: dict) -> None:
    seed_invoice_account(page, context, with_tax=True)
    set_late_fee_settings(
        context, enabled=True, amount="10", percent="10", fee_type="percent", days="5",
    )
