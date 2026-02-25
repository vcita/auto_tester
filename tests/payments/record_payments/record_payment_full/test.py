# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/record_payments/record_payment_full/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re

from playwright.sync_api import Page


def _get_billing_scope(page: Page):
    billing_iframe = page.locator('iframe[title="angularjs"]')
    if billing_iframe.count() > 0:
        try:
            billing_iframe.first.wait_for(state="visible", timeout=5000)
            return page.frame_locator('iframe[title="angularjs"]')
        except Exception:
            return page
    return page


def _open_invoice(page: Page):
    if "/app/payments/orders" not in page.url:
        sales_button = page.locator('[data-qa="nav-sales"]')
        if sales_button.count() == 0:
            sales_button = page.get_by_role("button", name="Sales", exact=True).first
        else:
            sales_button = sales_button.first
        sales_button.wait_for(state="visible", timeout=45000)
        sales_button.click()
        page.wait_for_url("**/app/pos", timeout=45000, wait_until="domcontentloaded")

        billing_link = page.get_by_text("Billing & Invoicing", exact=True)
        billing_link.wait_for(state="visible", timeout=45000)
        billing_link.click()
        page.wait_for_url("**/app/payments/orders", timeout=45000, wait_until="domcontentloaded")

    billing_scope = _get_billing_scope(page)
    invoice_link = billing_scope.get_by_role("link", name=re.compile("INVOICE #")).first
    invoice_link.wait_for(state="visible", timeout=45000)
    invoice_link.click()
    page.wait_for_url("**/app/invoices/**", timeout=45000, wait_until="domcontentloaded")
    return _get_billing_scope(page)


def _open_record_payment_dialog(invoice_scope):
    take_payment = invoice_scope.get_by_role(
        "button", name=re.compile(r"^Take payment")
    )
    take_payment.wait_for(state="visible", timeout=45000)
    take_payment.click()

    record_payment = invoice_scope.get_by_role(
        "menuitem", name=re.compile("Record payment")
    )
    record_payment.wait_for(state="visible", timeout=45000)
    record_payment.click()

    dialog = invoice_scope.get_by_role("dialog", name=re.compile("Record payment"))
    dialog.wait_for(state="visible", timeout=45000)
    return dialog


def test_record_payment_full(page: Page, context: dict) -> None:
    """
    Record a full payment for an invoice.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - recorded_payment_id
    - recorded_payment_amount
    - recorded_payment_method
    """
    invoice_scope = _open_invoice(page)
    dialog = _open_record_payment_dialog(invoice_scope)

    method_listbox = dialog.get_by_role("listbox", name="Payment received via")
    method_listbox.wait_for(state="visible", timeout=45000)
    method_listbox.click()
    dialog.get_by_role("option", name="Cash").click()

    record_button = dialog.get_by_role("button", name="Record")
    record_button.wait_for(state="visible", timeout=45000)
    record_button.click()

    dialog.wait_for(state="hidden", timeout=45000)

    paid_text = invoice_scope.get_by_text("Paid", exact=False)
    context["recorded_payment_id"] = page.url.split("/")[-1]
    context["recorded_payment_method"] = "Cash"
    context["recorded_payment_amount"] = (
        "full" if paid_text.count() > 0 else "unknown"
    )

