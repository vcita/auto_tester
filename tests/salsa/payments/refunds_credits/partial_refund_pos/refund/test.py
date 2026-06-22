import re

from playwright.sync_api import Page

from tests.salsa.payments.refunds_credits.partial_refund_helpers import (
    FAST_UI_TIMEOUT,
    assert_payment_page,
    partial_refund_current_payment,
)

ITEM_NAME = "custom_item"
ITEM_PRICE = "5"
PAYMENT_NAME = "Payment for Sale #1 - custom_item"
DIALOG_TIMEOUT = 30000


def _open_checkout(page: Page) -> None:
    if "/app/pos" in page.url:
        return
    checkout_link = page.get_by_text("Checkout", exact=True).first
    if checkout_link.count() > 0 and checkout_link.is_visible():
        checkout_link.click()
        page.wait_for_url("**/app/pos**", timeout=DIALOG_TIMEOUT, wait_until="domcontentloaded")
        return
    sales = page.locator('[data-qa="nav-sales"]')
    if sales.count() == 0:
        sales = page.get_by_role("button", name="Sales", exact=True).first
    else:
        sales = sales.first
    sales.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    sales.click()
    checkout_link = page.get_by_text("Checkout", exact=True).first
    checkout_link.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    checkout_link.click()
    page.wait_for_url("**/app/pos**", timeout=DIALOG_TIMEOUT, wait_until="domcontentloaded")


def _add_custom_item(page: Page) -> None:
    custom_item_button = page.get_by_role("button", name="Custom Item")
    custom_item_button.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    custom_item_button.click()

    name_field = page.get_by_role("textbox", name="Name*")
    name_field.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    name_field.click()
    name_field.press_sequentially(ITEM_NAME)

    price_field = page.get_by_role("spinbutton", name="Price*")
    price_field.click()
    price_field.press_sequentially(ITEM_PRICE)

    page.get_by_role("button", name="Add").click()


def _select_client(page: Page, context: dict) -> None:
    select_client = page.get_by_role("button", name=re.compile(r"^Select (Client|Property)$", re.I))
    select_client.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    select_client.click()

    iframe = page.frame_locator('iframe[title="angularjs"]')
    dialog = iframe.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    client = dialog.get_by_text(context.get("created_client_name"), exact=False).first
    client.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    client.click()
    dialog.wait_for(state="hidden", timeout=DIALOG_TIMEOUT)


def _checkout_and_record(page: Page) -> None:
    page.get_by_role("button", name="Checkout").click()

    menu = page.get_by_role("menu")
    menu.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    menu.get_by_text("Record payment").click()

    iframe = page.frame_locator('iframe[title="angularjs"]')
    record_dialog = iframe.get_by_role("dialog")
    record_dialog.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    method_listbox = iframe.get_by_role("listbox", name="Payment received via")
    method_listbox.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    method_listbox.click()
    iframe.get_by_role("option", name="Cash").click()
    record_button = iframe.get_by_role("button", name="Record")
    record_button.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    record_button.click()
    page.wait_for_url(
        "**/app/payments/transactions/**",
        timeout=DIALOG_TIMEOUT,
        wait_until="domcontentloaded",
    )


def test_pos_partial_refund(page: Page, context: dict) -> None:
    page.set_default_timeout(FAST_UI_TIMEOUT)

    print("  Step 1: Open Checkout (POS)")
    _open_checkout(page)
    print("  Step 2: Add custom item priced 5")
    _add_custom_item(page)
    print("  Step 3: Select client")
    _select_client(page, context)
    print("  Step 4: Checkout and record cash payment (lands on payment page)")
    _checkout_and_record(page)

    print("  Step 5: Partial refund of 1")
    partial_refund_current_payment(page, "1")
    print("  Step 6: Verify payment page amount and refund")
    assert_payment_page(page, PAYMENT_NAME, "$5.00", "-$1.00")
    print("  POS partial refund verified")
