# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/refunds_credits/issue_credit_note/script.md
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
        sales_button.wait_for(state="visible", timeout=5000)
        sales_button.click()
        page.wait_for_url("**/app/pos", timeout=5000, wait_until="domcontentloaded")

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


def test_issue_credit_note(page: Page, context: dict) -> None:
    """
    Issue a credit note when supported.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - issued_credit_note_id
    - issued_credit_note_amount
    """
    invoice_scope = _open_invoice(page)

    menu_button = invoice_scope.locator("md-menu").filter(
        has_text=re.compile("Edit")
    ).get_by_role("button")
    menu_button.wait_for(state="visible", timeout=5000)
    menu_button.click()

    credit_item = invoice_scope.get_by_role(
        "menuitem", name=re.compile("Credit note|Issue credit")
    )
    if credit_item.count() == 0:
        context["issued_credit_note_id"] = ""
        context["issued_credit_note_amount"] = ""
        context["credit_note_status"] = "not_supported"
        return

    credit_item.first.click()
    dialog = invoice_scope.get_by_role("dialog")

    amount_input = dialog.get_by_role("textbox").first
    amount_input.click()
    page.keyboard.press("ControlOrMeta+A")
    amount_input.press_sequentially("5", delay=30)

    reason_input = dialog.get_by_role("textbox").last
    if reason_input.count() > 0:
        reason_input.click()
        reason_input.press_sequentially("Test credit note", delay=30)

    save_button = dialog.get_by_role("button", name=re.compile("Save|Issue|Create"))
    if save_button.count() > 0:
        save_button.first.click()

    context["issued_credit_note_id"] = page.url.split("/")[-1]
    context["issued_credit_note_amount"] = "5"
    context["credit_note_status"] = "issued"

