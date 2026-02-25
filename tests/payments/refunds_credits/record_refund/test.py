# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/refunds_credits/record_refund/script.md
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


def test_record_refund(page: Page, context: dict) -> None:
    """
    Record a refund when supported.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - recorded_refund_id
    - recorded_refund_amount
    """
    invoice_scope = _open_invoice(page)

    refund_action = invoice_scope.get_by_text("Refund", exact=False)
    if refund_action.count() == 0:
        context["recorded_refund_id"] = ""
        context["recorded_refund_amount"] = ""
        context["refund_status"] = "not_supported"
        return

    refund_action.first.click()
    dialog = invoice_scope.get_by_role("dialog")
    amount_input = dialog.get_by_role("textbox").first
    amount_input.click()
    page.keyboard.press("ControlOrMeta+A")
    amount_input.press_sequentially("5", delay=30)

    save_button = dialog.get_by_role("button", name=re.compile("Save|Refund|Record"))
    if save_button.count() > 0:
        save_button.first.click()

    context["recorded_refund_id"] = page.url.split("/")[-1]
    context["recorded_refund_amount"] = "5"
    context["refund_status"] = "recorded"

