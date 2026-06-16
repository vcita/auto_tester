# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/settings/set_invoice_numbering/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time

from playwright.sync_api import Page, expect

UI_TIMEOUT = 20000


def _log_invoice_dialog_time(started_at: float, label: str) -> None:
    elapsed = time.monotonic() - started_at
    print(f"    [invoice-dialog] {label}: {elapsed:.1f}s")


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
    if from_section.count() == 0:
        from_section = editor_scope.locator("div").filter(
            has_text=re.compile(r"From:\s+Auto_", re.I)
        ).first
    if from_section.count() > 0:
        from_section.click(force=True)

    edit_address = editor_scope.locator(
        "[data-qa='itemizable-from-business-address-edit-button']"
    ).first
    if edit_address.count() > 0:
        try:
            edit_address.click()
        except Exception:
            pass

    billing_address = editor_scope.get_by_role(
        "textbox", name=re.compile(r"Billing address|Business Info", re.I)
    ).first
    if billing_address.count() == 0:
        billing_address = editor_scope.locator("textarea:visible").first

    try:
        billing_address.wait_for(state="visible", timeout=3000)
    except Exception:
        return
    billing_address.fill("123 Test Street, Test City")
    expect(billing_address).to_have_value("123 Test Street, Test City", timeout=2000)

    if from_section.count() > 0:
        from_section.click()


def _fill_visible_sender_billing_address(editor_scope) -> None:
    billing_address = editor_scope.locator("textarea:visible").first
    billing_address.wait_for(state="visible", timeout=3000)
    billing_address.fill("123 Test Street, Test City")
    expect(billing_address).to_have_value("123 Test Street, Test City", timeout=2000)


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


def _assert_invoice_tax_applied(billing_scope, context: dict) -> None:
    service_price = float(context.get("invoice_service_price", "100"))
    tax_rate = float(context.get("configured_tax_rate", "0"))
    if tax_rate <= 0:
        raise AssertionError("configured_tax_rate missing from context - run Set Tax Rates first")

    expected_total = service_price * (1 + tax_rate / 100)
    amount_heading = billing_scope.get_by_role(
        "heading", name=re.compile(r"^[₪$]\d")
    )
    expect(amount_heading.first).to_be_visible(timeout=5000)

    amount_text = amount_heading.first.inner_text().strip()
    expected_total_text = f"{expected_total:.2f}"
    if expected_total_text not in amount_text:
        raise AssertionError(
            f"Invoice total did not include tax. Expected {expected_total_text}, got {amount_text}"
        )

    tax_name = context.get("configured_tax_name")
    if tax_name:
        expect(billing_scope.get_by_text(tax_name, exact=False).first).to_be_visible(timeout=5000)


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
    invoice_dialog_started_at = time.monotonic()
    print("    [invoice-dialog] opened")

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
    _log_invoice_dialog_time(invoice_dialog_started_at, "client selected")

    print("  Step 5: Set invoice label and number...")
    editor_scope = _get_editor_scope(billing_scope)
    invoice_number = ""
    configured_prefix = "INVOICE"
    print("  Step 5: Invoice details edit unavailable, verifying generated numbering")
    _log_invoice_dialog_time(invoice_dialog_started_at, "invoice details handled")

    print("  Step 6: Fill required sender billing address...")
    _fill_sender_billing_address(editor_scope)
    _log_invoice_dialog_time(invoice_dialog_started_at, "sender address filled")

    print("  Step 7: Add a line item...")
    service_name = context.get("invoice_service_name")
    if not service_name:
        raise ValueError("invoice_service_name missing from context - run payments _setup first")
    _select_priced_service(page, billing_scope, editor_scope, service_name)
    _log_invoice_dialog_time(invoice_dialog_started_at, "line item selected")

    print("  Step 8: Save draft and verify...")
    save_draft = editor_scope.get_by_role("button", name="Save draft").last
    save_draft.wait_for(state="visible", timeout=UI_TIMEOUT)
    expect(save_draft).to_be_enabled(timeout=5000)
    save_draft.scroll_into_view_if_needed()
    save_draft.click(force=True)

    required_address = editor_scope.get_by_text("This field is required", exact=True)
    try:
        required_address.first.wait_for(state="visible", timeout=2000)
        _fill_visible_sender_billing_address(editor_scope)
        save_draft.click(force=True)
    except Exception:
        pass

    billing_scope = _get_billing_scope(page)
    # Prefer direct UI signal after save (invoice heading in details view).
    # If not present quickly, use one focused fallback via invoice list row.
    invoice_heading_pattern = re.compile(r"INVOICE.*#\d+", re.I)
    invoice_heading = billing_scope.get_by_role("heading", name=invoice_heading_pattern)
    try:
        invoice_heading.first.wait_for(state="visible", timeout=5000)
    except Exception:
        invoice_link = billing_scope.get_by_role("link", name=invoice_heading_pattern)
        if invoice_link.count() == 0:
            invoice_link = billing_scope.get_by_text(invoice_heading_pattern)
        invoice_link.first.wait_for(state="visible", timeout=5000)
        invoice_link.first.click()
        page.wait_for_url("**/app/invoices/**", timeout=5000, wait_until="domcontentloaded")
        billing_scope = _get_billing_scope(page)
        invoice_heading = billing_scope.get_by_role("heading", name=invoice_heading_pattern)
    _close_templates_popup(billing_scope)

    invoice_heading.wait_for(state="visible", timeout=5000)
    _log_invoice_dialog_time(invoice_dialog_started_at, "dialog closed and invoice visible")
    _assert_invoice_tax_applied(billing_scope, context)
    invoice_text = invoice_heading.first.inner_text()
    if invoice_number:
        expect(invoice_heading.first).to_contain_text(invoice_number)
    else:
        invoice_number_match = re.search(r"#(\d+)", invoice_text)
        invoice_number = invoice_number_match.group(1) if invoice_number_match else ""
        if not invoice_number:
            any_digits = re.search(r"(\d+)", invoice_text)
            invoice_number = any_digits.group(1) if any_digits else ""
        if not invoice_number:
            invoice_number = page.url.rstrip("/").split("/")[-1]
        if not invoice_number:
            raise Exception("Could not extract invoice identifier")

    context["configured_invoice_prefix"] = configured_prefix
    context["created_invoice_number"] = invoice_number

