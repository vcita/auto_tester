# Auto-generated from script.md
# Last updated: 2026-03-04
# Source: tests/payments/record_payments/record_payment_full/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import time

from playwright.sync_api import Page


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
    sales_button = page.locator('[data-qa="nav-sales"]')
    if sales_button.count() == 0:
        sales_button = page.get_by_role("button", name="Sales", exact=True).first
    else:
        sales_button = sales_button.first
    sales_button.wait_for(state="visible", timeout=5000)
    sales_button.click()
    page.wait_for_url("**/app/pos**", timeout=30000, wait_until="domcontentloaded")

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
    select_property = page.get_by_role("button", name="Select Property")
    select_property.wait_for(state="visible", timeout=30000)
    select_property.click()

    iframe = page.frame_locator('iframe[title="angularjs"]')
    dialog = iframe.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=30000)

    recently_active_list = dialog.get_by_role("list").nth(1)
    first_client = recently_active_list.get_by_role("listitem").first
    first_client.click()

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
