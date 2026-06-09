# Set Up Invoice Late Fee (UI + Client Portal)
# Migrated from automation-js/features/steps/payments-settings/invoice-settings.feature
# Scenario: "Set up invoice late fee" (VCITA2-13991)
# Source: tests/payments/invoices/invoice_late_fee_ui/set_late_fee_invoice/script.md

from playwright.sync_api import Page

from tests.payments.invoices.invoice_billing_ui import (
    assert_invoice_page,
    create_and_send_invoice,
)
from tests.payments.invoices.invoice_late_fee_ui.invoice_cp_ui import (
    assert_cp_invoice,
    open_pending_invoice,
    open_portal,
)
from tests.payments.invoices.invoice_late_fee_ui.late_fee_settings_ui import (
    assert_late_fee_enabled,
    set_amount_late_fee,
)

INVOICE_NAME = "new_invoice"
INVOICE_DISPLAY = "new_invoice #0000001"
CLIENT = "first last"
AMOUNT = "$100.00"


def test_set_late_fee_invoice(page: Page, context: dict) -> None:
    """Set amount-based late-fee settings via the UI, create+send an invoice with late fee
    enabled, verify the business-side invoice page, then verify the client-portal invoice
    page shows the late-fee caption."""
    service_name = context["invoice_service_name"]
    portal_token = context["client_portal_token"]

    print("  Step 1: Set late-fee settings (amount=10, after 5 days) via the settings UI")
    set_amount_late_fee(page, amount="10", days="5")
    assert_late_fee_enabled(page)

    print("  Step 2: Create and send an invoice with late fee enabled")
    create_and_send_invoice(
        page, context,
        name=INVOICE_NAME, client_name=CLIENT,
        billing_address="blablablabla",
        existing_items=[service_name],
        enable_late_fee=True,
    )

    print("  Step 3: Verify the business-side invoice page")
    assert_invoice_page(
        page, context,
        title=INVOICE_NAME, number=1, client=CLIENT,
        state="ISSUED", amount=AMOUNT, late_fee="Subject to late fees",
    )

    print("  Step 4: Client opens the pending invoice in the client portal")
    cp_page, cp_context = open_portal(page, context, portal_token)
    try:
        open_pending_invoice(cp_page, INVOICE_DISPLAY)

        print("  Step 5: Verify the client-portal invoice page shows 'Late fees'")
        assert_cp_invoice(
            cp_page,
            invoice_name=INVOICE_DISPLAY, client=CLIENT, price=AMOUNT, late_fee="Late fees",
        )
    finally:
        cp_context.close()
