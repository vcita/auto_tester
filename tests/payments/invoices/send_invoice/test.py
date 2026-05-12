# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/invoices/send_invoice/script.md
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
    if "/app/invoices/" in page.url:
        return _get_billing_scope(page)

    if "/app/payments/orders" not in page.url:
        sales_button = page.locator('[data-qa="nav-sales"]')
        if sales_button.count() == 0:
            sales_button = page.get_by_role("button", name="Sales", exact=True).first
        else:
            sales_button = sales_button.first
        sales_button.wait_for(state="visible", timeout=5000)
        sales_button.click()
        page.wait_for_url("**/app/pos**", timeout=5000, wait_until="domcontentloaded")

        billing_link = page.get_by_text("Billing & Invoicing", exact=True)
        billing_link.wait_for(state="visible", timeout=5000)
        billing_link.click()
        page.wait_for_url("**/app/payments/orders", timeout=5000, wait_until="domcontentloaded")

    billing_scope = _get_billing_scope(page)
    invoice_link = billing_scope.get_by_role("link", name=re.compile("INVOICE #")).first
    invoice_link.wait_for(state="visible", timeout=5000)
    invoice_link.click()
    page.wait_for_url("**/app/invoices/**", timeout=5000, wait_until="domcontentloaded")
    return _get_billing_scope(page)


def test_send_invoice(page: Page, context: dict) -> None:
    """
    Send or resend an invoice and record status.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - sent_invoice_status
    """
    invoice_scope = _open_invoice(page)

    send_button = invoice_scope.get_by_role("button", name="Send reminder")
    if send_button.count() > 0:
        send_button.first.click()
        dialog = invoice_scope.get_by_role("dialog")
        resend = dialog.get_by_role("button", name=re.compile("Send|Resend"))
        resend.wait_for(state="visible", timeout=5000)
        resend.click()

    status_text = invoice_scope.get_by_text("Invoice sent", exact=False)
    if status_text.count() > 0:
        context["sent_invoice_status"] = "sent"
        return

    issued_text = invoice_scope.get_by_text("Issued", exact=False)
    context["sent_invoice_status"] = "issued" if issued_text.count() > 0 else "unknown"

