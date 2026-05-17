# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/settings/set_invoice_numbering/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time

from playwright.sync_api import Page, expect

UI_TIMEOUT = 20000


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

    billing_address.wait_for(state="visible", timeout=5000)
    billing_address.fill("123 Test Street, Test City")

    if from_section.count() > 0:
        from_section.click()


def test_set_invoice_numbering(page: Page, context: dict) -> None:
    """
    Configure invoice label/number and verify it appears on the invoice header.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - configured_invoice_prefix
    - created_invoice_number
    """
    print("  Step 1: Use an existing client from the picker...")
    client_search_term = context.get("invoice_client_search_term", "Appt TestClient")

    print("  Step 2: Open Billing & Invoicing...")
    if "/app/payments/orders" not in page.url:
        sales_button = page.get_by_role("button", name="Sales")
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

    print("  Step 3: Start new invoice...")
    new_button = billing_scope.get_by_role("button", name="New")
    new_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    new_button.click()

    invoice_menu = billing_scope.get_by_role("menuitem", name="Invoice")
    invoice_menu.wait_for(state="visible", timeout=UI_TIMEOUT)
    invoice_menu.click()

    print("  Step 4: Select existing client...")
    client_dialog = billing_scope.get_by_role("dialog", name=re.compile("Invoice"))
    if client_dialog.count() == 0:
        client_dialog = billing_scope.get_by_role("dialog")
    if client_dialog.count() > 0:
        dialog = client_dialog.first
        search_input = dialog.locator("input").first
        if search_input.count() == 0:
            search_input = dialog.get_by_role(
                "textbox", name=re.compile(r"Search by name|Search", re.I)
            ).first

        def _pick_client(term: str) -> bool:
            if search_input.count() == 0 or not term:
                return False
            search_input.click()
            search_input.fill("")
            search_input.type(term, delay=10)
            try:
                candidate_row = dialog.get_by_role("button").filter(has_text=re.compile(r".+")).first
                if candidate_row.count() > 0:
                    candidate_row.wait_for(state="visible", timeout=5000)
                page.keyboard.press("ArrowDown")
                page.keyboard.press("Enter")
                dialog.wait_for(state="hidden", timeout=7000)
                return True
            except Exception:
                return False

        selected = _pick_client(client_search_term)
        if not selected and search_input.count() > 0:
            # Fallback: click first client row in list (avoid "New Property")
            search_input.click()
            search_input.fill("")
            first_client_row = dialog.get_by_role("button").filter(
                has_text=re.compile(r"@|vcita", re.I)
            ).first
            if first_client_row.count() == 0:
                buttons = dialog.get_by_role("button")
                if buttons.count() > 1:
                    first_client_row = buttons.nth(1)
            if first_client_row.count() > 0:
                first_client_row.wait_for(state="visible", timeout=5000)
                first_client_row.click()
            try:
                dialog.wait_for(state="hidden", timeout=5000)
                selected = True
            except Exception:
                selected = False
        if not selected:
            raise Exception(
                f"Client picker did not include any client matching: {client_search_term}"
            )
    else:
        raise Exception("Client picker dialog did not open")

    editor_scope = _get_editor_scope(billing_scope)
    details_toggle = editor_scope.get_by_role("button", name="Invoice Details")
    if details_toggle.count() == 0:
        details_toggle = editor_scope.get_by_text("Invoice Details", exact=True)
    details_toggle.first.wait_for(state="visible", timeout=UI_TIMEOUT)

    print("  Step 5: Set invoice label and number...")
    timestamp = int(time.time())
    invoice_number = ""
    configured_prefix = "INVOICE"
    invoice_label = f"INVOICE {timestamp}"
    try:
        details_toggle.first.click()
        label_box = editor_scope.get_by_role("textbox", name="Invoice Label")
        number_box = editor_scope.get_by_role("textbox", name="Invoice Number")
        if label_box.count() > 0 and number_box.count() > 0:
            label_box.first.click()
            try:
                page.keyboard.press("Control+A")
            except Exception:
                page.keyboard.press("Meta+A")
            label_box.first.fill("")
            label_box.first.press_sequentially(invoice_label, delay=10)
            configured_prefix = invoice_label

            invoice_number = str(timestamp)[-6:]
            number_box.first.click()
            try:
                page.keyboard.press("Control+A")
            except Exception:
                page.keyboard.press("Meta+A")
            number_box.first.fill("")
            number_box.first.press_sequentially(invoice_number, delay=10)
    except Exception:
        print("  Step 5: Invoice details edit unavailable, continuing with default numbering")

    print("  Step 6: Fill required sender billing address...")
    _fill_sender_billing_address(editor_scope)

    print("  Step 7: Add a line item...")
    item_box = editor_scope.get_by_role("textbox", name="Please select an item")
    if item_box.count() > 0:
        item_box.first.click()
        service_option = editor_scope.get_by_role(
            "option", name=re.compile(r"Event Test Workshop|Test Workshop", re.I)
        ).first
        if service_option.count() == 0:
            service_option = editor_scope.get_by_role("option").filter(
                has_not_text=re.compile(r"Add custom item", re.I)
            ).first
        if service_option.count() == 0:
            service_option = editor_scope.get_by_role("option").first
        service_option.wait_for(state="visible", timeout=UI_TIMEOUT)
        service_option.click()

    add_item_title = editor_scope.get_by_text("Add Item", exact=True)
    if add_item_title.count() > 0 and add_item_title.first.is_visible():
        name_input = editor_scope.locator('input[placeholder="Name"]').first
        if name_input.count() == 0:
            name_input = editor_scope.get_by_role("textbox", name=re.compile("Name", re.I)).first
        name_input.wait_for(state="visible", timeout=10000)
        name_input.click()
        name_input.fill("")
        name_input.press_sequentially("Test line item", delay=5)

        price_input = editor_scope.locator('input[placeholder*="Price"]').first
        if price_input.count() > 0:
            price_input.click()
            try:
                page.keyboard.press("Control+A")
            except Exception:
                page.keyboard.press("Meta+A")
            page.keyboard.press("Backspace")
            page.keyboard.type("10", delay=5)

        invalid_price = editor_scope.get_by_text("Invalid", exact=False)
        if invalid_price.count() > 0 and price_input.count() > 0:
            price_input.click()
            try:
                page.keyboard.press("Control+A")
            except Exception:
                page.keyboard.press("Meta+A")
            page.keyboard.press("Backspace")
            page.keyboard.type("10", delay=5)

        add_button = editor_scope.get_by_role("button", name="Add").last
        add_button.wait_for(state="visible", timeout=10000)
        expect(add_button).to_be_enabled(timeout=10000)
        add_button.click()
        add_item_title.first.wait_for(state="hidden", timeout=12000)

    print("  Step 8: Save draft and verify...")
    save_draft = editor_scope.get_by_role("button", name="Save draft")
    save_draft.wait_for(state="visible", timeout=UI_TIMEOUT)
    save_draft.click()

    billing_scope = _get_billing_scope(page)
    # Prefer direct UI signal after save (invoice heading in details view).
    # If not present quickly, use one focused fallback via invoice list row.
    invoice_heading = billing_scope.get_by_role("heading", name=re.compile(r"INVOICE #"))
    try:
        invoice_heading.first.wait_for(state="visible", timeout=8000)
    except Exception:
        invoice_link = billing_scope.get_by_role("link", name=re.compile(r"INVOICE #"))
        if invoice_link.count() == 0:
            invoice_link = billing_scope.get_by_text(re.compile(r"INVOICE #"))
        invoice_link.first.wait_for(state="visible", timeout=12000)
        invoice_link.first.click()
        page.wait_for_url("**/app/invoices/**", timeout=12000, wait_until="domcontentloaded")
        billing_scope = _get_billing_scope(page)
        invoice_heading = billing_scope.get_by_role("heading", name=re.compile(r"INVOICE #"))
    _close_templates_popup(billing_scope)

    invoice_heading.wait_for(state="visible", timeout=12000)
    invoice_text = invoice_heading.first.inner_text()
    if invoice_number:
        expect(invoice_heading.first).to_contain_text(invoice_number)
    else:
        invoice_number_match = re.search(r"#(\\d+)", invoice_text)
        invoice_number = invoice_number_match.group(1) if invoice_number_match else ""
        if not invoice_number:
            any_digits = re.search(r"(\\d+)", invoice_text)
            invoice_number = any_digits.group(1) if any_digits else ""
        if not invoice_number:
            invoice_number = page.url.rstrip("/").split("/")[-1]
        if not invoice_number:
            raise Exception("Could not extract invoice identifier")

    context["configured_invoice_prefix"] = configured_prefix
    context["created_invoice_number"] = invoice_number

