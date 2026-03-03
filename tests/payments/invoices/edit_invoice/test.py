# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/invoices/edit_invoice/script.md
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


def _get_editor_scope(billing_scope):
    editor_iframe = billing_scope.locator("#vue_wizard_iframe")
    if editor_iframe.count() > 0:
        return billing_scope.frame_locator("#vue_wizard_iframe")
    return billing_scope


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


def test_edit_invoice(page: Page, context: dict) -> None:
    """
    Edit an invoice by adding another item and verify total changes.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - created_invoice_amount
    """
    invoice_scope = _open_invoice(page)

    amount_heading = invoice_scope.get_by_role("heading", name=re.compile(r"^₪\\d"))
    amount_heading.wait_for(state="visible", timeout=5000)
    original_amount = amount_heading.first.inner_text().strip()

    menu_button = invoice_scope.locator("md-menu").filter(
        has_text=re.compile("Edit")
    ).get_by_role("button")
    menu_button.wait_for(state="visible", timeout=5000)
    menu_button.click()

    edit_item = invoice_scope.get_by_role("menuitem", name="Edit")
    edit_item.wait_for(state="visible", timeout=5000)
    edit_item.click()

    editor_scope = _get_editor_scope(invoice_scope)
    item_box = editor_scope.get_by_role("textbox", name="Please select an item")
    item_box.wait_for(state="visible", timeout=5000)
    item_box.click()

    first_service = editor_scope.get_by_role(
        "option", name=re.compile(r"Event Test Workshop")
    ).first
    first_service.wait_for(state="visible", timeout=5000)
    first_service.click()

    save_button = editor_scope.get_by_role(
        "button", name=re.compile(r"Save draft|Save")
    )
    save_button.wait_for(state="visible", timeout=5000)
    save_button.click()

    page.wait_for_url("**/app/invoices/**", timeout=5000, wait_until="domcontentloaded")
    invoice_scope = _get_billing_scope(page)

    updated_heading = invoice_scope.get_by_role("heading", name=re.compile(r"^₪\\d"))
    updated_heading.wait_for(state="visible", timeout=5000)
    updated_amount = updated_heading.first.inner_text().strip()
    assert updated_amount != original_amount, "Invoice total did not change after edit"
    context["created_invoice_amount"] = updated_amount.replace("₪", "").strip()

