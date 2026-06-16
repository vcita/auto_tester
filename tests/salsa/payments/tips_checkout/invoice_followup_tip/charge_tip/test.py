# Migrated from automation-js/features/salsa/tips.feature (VCITA2-13899)
# Source: tests/payments/tips_checkout/invoice_followup_tip/charge_tip/script.md

from playwright.sync_api import Page

from tests.salsa.payments.tips_checkout.tips_checkout_bo import (
    add_followup_tip,
    assert_payment_page_with_tip,
    open_invoice_payment_page,
)


def test_charge_tip(page: Page, context: dict) -> None:
    """Add a 10% charge follow-up tip to a paid invoice (BO)."""
    store = context["tips_checkout"]
    invoice = store["invoice"]
    invoice_title = invoice["title"]

    print(f"  Open paid invoice '{invoice_title}' and add a 10% charge tip")
    open_invoice_payment_page(page, context, invoice["id"])
    add_followup_tip(page, context, tip_option="10%", payment_type="charge")

    assert_payment_page_with_tip(page, context, {
        "search": "first",
        "client_name": "first last",
        "name": f"Tip for {invoice_title}",
        "amount": "$2.00",
        "type": "Credit Card (Online)",
        "items": "product_item200",
        "tip": "$2.00",
    })
