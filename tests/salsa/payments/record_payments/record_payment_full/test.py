# Auto-generated from script.md
# Last updated: 2026-03-04
# Source: tests/payments/record_payments/record_payment_full/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time

from playwright.sync_api import Page, expect

SELECT_CLIENT_PATTERN = re.compile(r"^Select (Client|Property)$", re.I)
EMAIL_PATTERN = re.compile(r"@")


def _open_client_picker(page: Page):
    select_client = page.get_by_role("button", name=SELECT_CLIENT_PATTERN)
    select_client.wait_for(state="visible", timeout=30000)
    select_client.click()
    dialog = page.frame_locator('iframe[title="angularjs"]').get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=30000)
    return dialog


def _open_all_clients(dialog) -> None:
    """Switch the picker from 'Recently Active' to the full 'All Clients' list."""
    all_clients = dialog.get_by_text(re.compile(r"^\s*all clients\s*$", re.I)).first
    if all_clients.count() > 0:
        all_clients.click()


def _search_picker(page: Page, dialog, client_name: str) -> None:
    """Type the client name into the picker search box to surface the matching row."""
    search = dialog.get_by_role("textbox").first
    if search.count() == 0:
        return
    search.click()
    search.fill(client_name)
    page.wait_for_timeout(1200)


def _pick_client_row(dialog, client_name: str | None):
    """Return the client row to click.

    The picker renders Angular Material `md-list-item[role=listitem]` rows. The
    first row is a "New Client" action (no email), so we target the named row or
    the first real client row (one containing an email), never "New Client".
    """
    rows = dialog.get_by_role("listitem")
    if client_name:
        named = rows.filter(has_text=client_name).first
        if named.count() > 0:
            return named
    real_client = rows.filter(has_text=EMAIL_PATTERN).first
    return real_client if real_client.count() > 0 else None


def _select_checkout_client(page: Page, context: dict) -> None:
    """Select a client and confirm the selection actually registered.

    The previous `get_by_text(client_name).first` clicked a non-selectable text
    node, dismissing the picker without choosing a client and leaving Checkout
    disabled so the later click timed out (30s). We now click an actual client
    row and verify Checkout becomes enabled, retrying (searching on later
    attempts for not-yet-listed clients) before failing with a clear message.
    """
    client_name = context.get("created_client_name") or context.get("invoice_client_search_term")
    checkout_button = page.get_by_role("button", name="Checkout")

    for attempt in range(3):
        dialog = _open_client_picker(page)
        target = _pick_client_row(dialog, client_name)
        if target is None:
            _open_all_clients(dialog)
            if client_name:
                _search_picker(page, dialog, client_name)
            target = _pick_client_row(dialog, client_name)
        if target is not None:
            target.click()
            try:
                expect(checkout_button).to_be_enabled(timeout=8000)
                return
            except AssertionError:
                pass
        if dialog.is_visible():
            page.keyboard.press("Escape")

    raise AssertionError(
        "Client selection did not register in the Checkout client picker - "
        "Checkout stayed disabled after choosing a client."
    )


def _open_checkout(page: Page) -> None:
    if "/app/pos" in page.url:
        return

    checkout_link = page.get_by_text("Checkout", exact=True).first
    if checkout_link.count() > 0 and checkout_link.is_visible():
        checkout_link.click()
        page.wait_for_url("**/app/pos**", timeout=30000, wait_until="domcontentloaded")
        return

    sales_button = page.locator('[data-qa="nav-sales"]')
    if sales_button.count() == 0:
        sales_button = page.get_by_role("button", name="Sales", exact=True).first
    else:
        sales_button = sales_button.first
    sales_button.wait_for(state="visible", timeout=5000)
    sales_button.click()

    try:
        page.wait_for_url("**/app/pos**", timeout=5000, wait_until="domcontentloaded")
        return
    except Exception:
        pass

    checkout_link = page.get_by_text("Checkout", exact=True).first
    checkout_link.wait_for(state="visible", timeout=5000)
    checkout_link.click()
    page.wait_for_url("**/app/pos**", timeout=30000, wait_until="domcontentloaded")


def test_record_payment_full(page: Page, context: dict) -> None:
    """
    Record a full payment via the Checkout page and verify the payment record.

    Prerequisites:
    - User is logged in (from category _setup)
    - No payment gateway connected

    Saves to context:
    - recorded_payment_id
    - recorded_payment_amount
    - recorded_payment_method
    """
    item_name = f"Test Payment {int(time.time())}"
    item_price = "50"

    # Step 1: Navigate to Checkout
    print("  Step 1: Navigate to Checkout...")
    _open_checkout(page)

    # Step 2: Add a Custom Item with a cost
    print("  Step 2: Add Custom Item...")
    custom_item_button = page.get_by_role("button", name="Custom Item")
    custom_item_button.wait_for(state="visible", timeout=30000)
    custom_item_button.click()

    name_field = page.get_by_role("textbox", name="Name*")
    name_field.wait_for(state="visible", timeout=30000)
    name_field.click()
    page.wait_for_timeout(100)
    name_field.press_sequentially(item_name)

    price_field = page.get_by_role("spinbutton", name="Price*")
    price_field.click()
    price_field.press_sequentially(item_price)

    add_button = page.get_by_role("button", name="Add")
    add_button.wait_for(state="visible", timeout=30000)
    add_button.click()

    # Step 3: Select a client
    print("  Step 3: Select client...")
    _select_checkout_client(page, context)

    # Step 4: Click Checkout
    print("  Step 4: Click Checkout...")
    checkout_button = page.get_by_role("button", name="Checkout")
    checkout_button.wait_for(state="visible", timeout=30000)
    checkout_button.click()

    # Step 5: Select "Record payment"
    print("  Step 5: Select Record payment...")
    menu = page.get_by_role("menu")
    menu.wait_for(state="visible", timeout=30000)
    record_payment_option = menu.get_by_text("Record payment")
    record_payment_option.click()

    # Step 6: Select Cash payment method and click Record
    print("  Step 6: Select Cash and Record...")
    iframe = page.frame_locator('iframe[title="angularjs"]')

    record_dialog = iframe.get_by_role("dialog")
    record_dialog.wait_for(state="visible", timeout=30000)

    method_listbox = iframe.get_by_role("listbox", name="Payment received via")
    method_listbox.wait_for(state="visible", timeout=30000)
    method_listbox.click()

    cash_option = iframe.get_by_role("option", name="Cash")
    cash_option.click()

    record_button = iframe.get_by_role("button", name="Record")
    record_button.wait_for(state="visible", timeout=30000)
    record_button.click()

    # Success Verification
    print("  Verifying payment...")
    page.wait_for_url(
        "**/app/payments/transactions/**",
        timeout=30000,
        wait_until="domcontentloaded",
    )

    iframe = page.frame_locator('iframe[title="angularjs"]')

    paid_status = iframe.get_by_text("Paid", exact=True).first
    paid_status.wait_for(state="visible", timeout=30000)

    cash_indicator = iframe.get_by_text("Cash", exact=True)
    cash_indicator.wait_for(state="visible", timeout=30000)

    payment_id = page.url.split("/")[-1]
    context["recorded_payment_id"] = payment_id
    context["recorded_payment_amount"] = item_price
    context["recorded_payment_method"] = "Cash"

    print(f"  Payment recorded: id={payment_id}, amount={item_price}, method=Cash")
