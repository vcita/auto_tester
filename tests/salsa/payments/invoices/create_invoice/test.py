# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/invoices/create_invoice/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time

from playwright.sync_api import Page, expect

UI_TIMEOUT = 5000
# Save-draft triggers a backend write plus an angularjs+Vue wizard iframe remount
# before landing on /app/invoices/; under suite load that nav exceeds 5s. Matches the
# NAV_TIMEOUT used by the sibling invoice helpers (invoice_billing_ui.py).
NAV_TIMEOUT = 20000


def _get_billing_scope(page: Page):
    billing_iframe = page.locator('iframe[title="angularjs"]')
    if billing_iframe.count() > 0:
        try:
            billing_iframe.first.wait_for(state="visible", timeout=UI_TIMEOUT)
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


def _select_existing_client(page: Page, billing_scope, client_search_term: str) -> None:
    client_dialog = billing_scope.get_by_role("dialog", name=re.compile("Invoice"))
    if client_dialog.count() == 0:
        client_dialog = billing_scope.get_by_role("dialog")
    if client_dialog.count() == 0:
        raise Exception("Client picker dialog did not open")

    dialog = client_dialog.first
    search_input = dialog.locator("input").first
    if search_input.count() == 0:
        search_input = dialog.get_by_role(
            "textbox", name=re.compile(r"Search by name|Search", re.I)
        ).first

    if search_input.count() > 0 and client_search_term:
        search_input.click()
        search_input.fill("")
        search_input.type(client_search_term, delay=10)
        try:
            candidate_row = dialog.get_by_role("button").filter(
                has_text=re.compile(r".+")
            ).first
            if candidate_row.count() > 0:
                candidate_row.wait_for(state="visible", timeout=UI_TIMEOUT)
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            dialog.wait_for(state="hidden", timeout=UI_TIMEOUT)
            return
        except Exception:
            pass

    if search_input.count() > 0:
        search_input.click()
        search_input.fill("")
    first_client_row = dialog.get_by_role("button").filter(
        has_text=re.compile(r"@|vcita", re.I)
    ).first
    if first_client_row.count() == 0:
        buttons = dialog.get_by_role("button")
        if buttons.count() > 1:
            first_client_row = buttons.nth(1)
    if first_client_row.count() == 0:
        raise Exception(f"Client picker did not include any client matching: {client_search_term}")
    first_client_row.wait_for(state="visible", timeout=UI_TIMEOUT)
    first_client_row.click()
    dialog.wait_for(state="hidden", timeout=UI_TIMEOUT)


def _fill_sender_billing_address(editor_scope) -> None:
    from_section = editor_scope.locator("[data-qa='itemizable-from-fold']").first
    if from_section.count() > 0:
        from_section.click()

    edit_address = editor_scope.locator(
        "[data-qa='itemizable-from-business-address-edit-button']"
    ).first
    if edit_address.count() > 0:
        try:
            edit_address.click()
        except Exception:
            pass

    billing_address = editor_scope.locator(
        "[data-qa='itemizable-from-business-address-edit'] textarea"
    ).first
    if billing_address.count() == 0:
        billing_address = editor_scope.locator(
            'textarea[placeholder*="Billing address"], textarea'
        ).first

    billing_address.wait_for(state="visible", timeout=UI_TIMEOUT)
    billing_address.fill("123 Test Street, Test City")

    if from_section.count() > 0:
        from_section.click()


def _first_visible_locator(locators, timeout: int = UI_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for locator in locators:
            for index in range(locator.count()):
                candidate = locator.nth(index)
                try:
                    if candidate.is_visible():
                        return candidate
                except Exception:
                    continue
        time.sleep(0.1)
    return None


def _select_priced_service(page: Page, billing_scope, editor_scope, service_name: str) -> None:
    item_box = editor_scope.get_by_role("textbox", name="Please select an item")
    item_box.wait_for(state="visible", timeout=UI_TIMEOUT)
    item_box.click()

    service_option = _first_visible_locator(
        [
            scope.get_by_role("option", name=re.compile(re.escape(service_name), re.I))
            for scope in (page, billing_scope, editor_scope)
        ]
        + [
            scope.get_by_text(service_name, exact=True)
            for scope in (page, billing_scope, editor_scope)
        ]
    )
    if service_option is None:
        raise AssertionError(f"Invoice service option did not appear: {service_name}")

    service_option.click()


def _approve_draft_invoice(billing_scope) -> None:
    approve_button = billing_scope.locator('button[data-qa="approve"]').filter(
        has_text=re.compile(r"Approve draft", re.I)
    )
    if approve_button.count() == 0:
        approve_button = billing_scope.get_by_role(
            "button", name=re.compile(r"Approve draft", re.I)
        )

    approve_button.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    approve_button.first.click()

    dialog = billing_scope.get_by_role("dialog")
    if dialog.count() > 0:
        confirm = dialog.get_by_role(
            "button", name=re.compile(r"^(Approve|Confirm|Yes|Send|OK)$", re.I)
        )
        if confirm.count() > 0:
            confirm.first.click()

    billing_scope.get_by_text("DRAFT", exact=False).first.wait_for(
        state="hidden", timeout=UI_TIMEOUT
    )


def test_create_invoice(page: Page, context: dict) -> None:
    """
    Create a new invoice with a line item and approve it.

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
        billing_link = page.get_by_text("Billing & Invoicing", exact=True)
        if billing_link.count() > 0 and billing_link.first.is_visible():
            billing_link.first.click()
        else:
            sales_button = page.locator('[data-qa="nav-sales"]')
            if sales_button.count() == 0:
                sales_button = page.get_by_role("button", name="Sales", exact=True).first
            else:
                sales_button = sales_button.first
            sales_button.wait_for(state="visible", timeout=UI_TIMEOUT)
            sales_button.click()
            page.wait_for_url("**/app/pos**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")

            billing_link = page.get_by_text("Billing & Invoicing", exact=True)
            billing_link.wait_for(state="visible", timeout=UI_TIMEOUT)
            billing_link.click()
        page.wait_for_url("**/app/payments/orders", timeout=UI_TIMEOUT, wait_until="domcontentloaded")

    billing_scope = _get_billing_scope(page)

    close_empty_state = billing_scope.get_by_role("button", name="icon-close")
    if close_empty_state.count() > 0:
        close_empty_state.first.click()

    print("  Step 2: Start new invoice...")
    new_button = billing_scope.get_by_role("button", name="New")
    new_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    new_button.click()

    invoice_menu = billing_scope.get_by_role("menuitem", name="Invoice")
    invoice_menu.wait_for(state="visible", timeout=UI_TIMEOUT)
    invoice_menu.click()

    print("  Step 3: Select client...")
    client_search_term = context.get("invoice_client_search_term", "Appt TestClient")
    _select_existing_client(page, billing_scope, client_search_term)

    editor_scope = _get_editor_scope(billing_scope)
    editor_scope.get_by_role("textbox", name="Please select an item").wait_for(
        state="visible", timeout=UI_TIMEOUT
    )

    print("  Step 4: Fill required sender billing address...")
    _fill_sender_billing_address(editor_scope)

    print("  Step 5: Add line item...")
    service_name = context.get("invoice_service_name")
    if not service_name:
        raise ValueError("invoice_service_name missing from context - run payments _setup first")
    _select_priced_service(page, billing_scope, editor_scope, service_name)

    print("  Step 6: Save draft...")
    save_draft = editor_scope.get_by_role("button", name="Save draft")
    save_draft.wait_for(state="visible", timeout=UI_TIMEOUT)
    save_draft.click()

    page.wait_for_url("**/app/invoices/**", timeout=NAV_TIMEOUT, wait_until="domcontentloaded")
    billing_scope = _get_billing_scope(page)
    _close_templates_popup(billing_scope)

    print("  Step 7: Capture invoice details...")
    invoice_heading = billing_scope.get_by_role(
        "heading", name=re.compile(r"INVOICE #")
    )
    invoice_heading.wait_for(state="visible", timeout=UI_TIMEOUT)
    invoice_text = invoice_heading.first.inner_text()
    invoice_number_match = re.search(r"#(\d+)", invoice_text)
    invoice_number = invoice_number_match.group(1) if invoice_number_match else ""

    amount_heading = billing_scope.get_by_role(
        "heading", name=re.compile(r"^[₪$]\d")
    )
    amount_heading.wait_for(state="visible", timeout=UI_TIMEOUT)
    amount_text = amount_heading.first.inner_text().strip()
    amount_value = amount_text.replace("₪", "").replace("$", "").strip()
    if amount_value in {"0", "0.00"}:
        raise AssertionError("Created invoice total stayed at zero after adding line item")

    invoice_id = page.url.rstrip("/").split("/")[-1]

    expect(invoice_heading.first).to_be_visible()
    expect(amount_heading.first).to_be_visible()

    print("  Step 8: Approve draft invoice...")
    _approve_draft_invoice(billing_scope)

    context["created_invoice_id"] = invoice_id
    context["created_invoice_number"] = invoice_number
    context["created_invoice_amount"] = amount_value
    context["created_invoice_status"] = "issued"

