# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/invoices/create_invoice/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re

from playwright.sync_api import Page, expect


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


def _close_templates_popup(billing_scope) -> None:
    close_button = billing_scope.get_by_role("button", name="Close")
    if close_button.count() > 0:
        close_button.first.click()


def test_create_invoice(page: Page, context: dict) -> None:
    """
    Create a new invoice with a line item and save it as draft.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - created_invoice_id
    - created_invoice_number
    - created_invoice_amount
    """
    print("  Step 1: Open Billing & Invoicing...")
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

    close_empty_state = billing_scope.get_by_role("button", name="icon-close")
    if close_empty_state.count() > 0:
        close_empty_state.first.click()

    print("  Step 2: Start new invoice...")
    new_button = billing_scope.get_by_role("button", name="New")
    new_button.wait_for(state="visible", timeout=45000)
    new_button.click()

    invoice_menu = billing_scope.get_by_role("menuitem", name="Invoice")
    invoice_menu.wait_for(state="visible", timeout=45000)
    invoice_menu.click()

    print("  Step 3: Select client...")
    client_button = billing_scope.get_by_role(
        "button", name=re.compile("You as a client")
    )
    client_button.wait_for(state="visible", timeout=45000)
    client_button.click()

    editor_scope = _get_editor_scope(billing_scope)
    editor_scope.get_by_role("textbox", name="Please select an item").wait_for(
        state="visible", timeout=45000
    )

    print("  Step 4: Add line item...")
    item_box = editor_scope.get_by_role("textbox", name="Please select an item")
    item_box.click()
    first_service = editor_scope.get_by_role(
        "option", name=re.compile(r"Event Test Workshop")
    ).first
    first_service.wait_for(state="visible", timeout=45000)
    first_service.click()

    print("  Step 5: Save draft...")
    save_draft = editor_scope.get_by_role("button", name="Save draft")
    save_draft.wait_for(state="visible", timeout=45000)
    save_draft.click()

    page.wait_for_url("**/app/invoices/**", timeout=45000, wait_until="domcontentloaded")
    billing_scope = _get_billing_scope(page)
    _close_templates_popup(billing_scope)

    print("  Step 6: Capture invoice details...")
    invoice_heading = billing_scope.get_by_role(
        "heading", name=re.compile(r"INVOICE #")
    )
    invoice_heading.wait_for(state="visible", timeout=45000)
    invoice_text = invoice_heading.first.inner_text()
    invoice_number_match = re.search(r"#(\d+)", invoice_text)
    invoice_number = invoice_number_match.group(1) if invoice_number_match else ""

    amount_heading = billing_scope.get_by_role(
        "heading", name=re.compile(r"^[₪$]\d")
    )
    amount_heading.wait_for(state="visible", timeout=45000)
    amount_text = amount_heading.first.inner_text().strip()
    amount_value = amount_text.replace("₪", "").replace("$", "").strip()

    invoice_id = page.url.rstrip("/").split("/")[-1]

    expect(invoice_heading.first).to_be_visible()
    expect(amount_heading.first).to_be_visible()

    context["created_invoice_id"] = invoice_id
    context["created_invoice_number"] = invoice_number
    context["created_invoice_amount"] = amount_value

