import re
import time

from playwright.sync_api import Page

from tests.payments.refunds_credits.partial_refund_helpers import (
    FAST_UI_TIMEOUT,
    assert_payment_page,
    first_visible,
    open_payment_by_name,
    partial_refund_current_payment,
)

ITEM_NAME = "custom_item"
ITEM_AMOUNT = "5"
PAYMENT_NAME = "Payment for custom_item"
DIALOG_TIMEOUT = 30000


def _click_text_in_any_frame(page: Page, text: str, timeout: int = DIALOG_TIMEOUT) -> bool:
    """Find and click an element with the given text in any frame (dialogs may nest in vuetage)."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                locator = frame.get_by_text(text, exact=False).first
                if locator.count() > 0 and locator.is_visible():
                    try:
                        locator.click(timeout=FAST_UI_TIMEOUT)
                    except Exception:
                        locator.evaluate("(element) => element.click()")
                    return True
            except Exception:
                continue
        time.sleep(0.3)
    return False


def _open_record_payment_quick_action(page: Page) -> None:
    quick_actions = page.locator('[data-qa="vcMenu-QuickAction"]')
    if quick_actions.count() == 0:
        quick_actions = page.locator(".quick-actions button")
    quick_actions.first.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    quick_actions.first.click()

    record_item = page.locator('[data-qa="item-record_payment"]')
    record_item.wait_for(state="visible", timeout=DIALOG_TIMEOUT)
    record_item.click()


def _cancel_dialog(page: Page) -> None:
    if not _click_text_in_any_frame(page, "Cancel", timeout=3000):
        page.keyboard.press("Escape")
    time.sleep(1)


def _open_and_select_client(page: Page, context: dict) -> None:
    # The picker loads its client list once; a freshly created client may not be
    # indexed yet, so reopen the dialog and retry until the client appears.
    client_name = context["created_client_name"]
    for _ in range(5):
        _open_record_payment_quick_action(page)
        if _click_text_in_any_frame(page, client_name, timeout=6000):
            return
        _cancel_dialog(page)
        time.sleep(4)
    raise AssertionError("Client row did not appear in the Record payment picker after retries")


def _record_frame(page: Page, timeout: int = DIALOG_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.get_by_text("Service, package or product", exact=False).count() > 0:
                    return frame
            except Exception:
                continue
        time.sleep(0.3)
    return None


def _select_custom_item(page: Page, frame) -> None:
    service_field = first_visible(
        [
            frame.get_by_role("combobox"),
            frame.get_by_placeholder(re.compile(r"Service, package", re.I)),
            frame.get_by_text("Service, package or product", exact=False),
        ],
        timeout=8000,
    )
    if service_field is None:
        raise AssertionError("Service field not found")
    try:
        service_field.click(timeout=8000)
    except Exception:
        service_field.evaluate("(element) => element.click()")

    option = first_visible(
        [
            frame.get_by_role("option", name=re.compile(r"^Custom item$", re.I)),
            frame.get_by_text("Custom item", exact=True),
        ],
        timeout=8000,
    )
    if option is None:
        raise AssertionError("'Custom item' option not found")
    try:
        option.click(timeout=8000)
    except Exception:
        option.evaluate("(element) => element.click()")


def _fill_custom_item_name(frame) -> None:
    name_input = first_visible(
        [
            frame.get_by_placeholder("Item name"),
            frame.get_by_placeholder("Name"),
            frame.get_by_placeholder(re.compile(r"name", re.I)),
            frame.get_by_label(re.compile(r"item name", re.I)),
        ],
        timeout=8000,
    )
    if name_input is None:
        raise AssertionError("Custom item name field not found")
    name_input.fill(ITEM_NAME)


def _fill_record_payment_dialog(page: Page) -> None:
    frame = _record_frame(page)
    if frame is None:
        raise AssertionError("Record payment dialog frame not found")

    _select_custom_item(page, frame)
    _fill_custom_item_name(frame)

    amount_input = first_visible(
        [
            frame.get_by_label(re.compile(r"^Amount", re.I)),
            frame.get_by_placeholder("Amount"),
            frame.locator("input[type='number']"),
        ],
        timeout=8000,
    )
    if amount_input is None:
        raise AssertionError("Amount field not found")
    amount_input.fill(ITEM_AMOUNT)

    method_field = first_visible(
        [
            frame.get_by_role("combobox", name=re.compile(r"Payment method", re.I)),
            frame.get_by_text("Payment method", exact=False),
        ],
        timeout=8000,
    )
    if method_field is None:
        raise AssertionError("Payment method field not found")
    try:
        method_field.click(timeout=8000)
    except Exception:
        method_field.evaluate("(element) => element.click()")
    if not _click_text_in_any_frame(page, "Cash", timeout=8000):
        raise AssertionError("Cash payment method option not found")

    save = first_visible(
        [
            frame.locator('[data-qa="vc-footer-Save"]'),
            frame.get_by_role("button", name=re.compile(r"^Save$", re.I)),
        ],
        timeout=8000,
    )
    if save is None:
        raise AssertionError("Save button not found")
    save.click(timeout=FAST_UI_TIMEOUT)


def test_bo_partial_refund(page: Page, context: dict) -> None:
    page.set_default_timeout(FAST_UI_TIMEOUT)

    print("  Step 1-2: Open Quick Actions -> Record payment and select client")
    _open_and_select_client(page, context)
    print("  Step 3: Record custom-item cash payment of 5")
    _fill_record_payment_dialog(page)

    print("  Step 4: Open payment in Payments Received")
    open_payment_by_name(page, context["created_client_name"], PAYMENT_NAME)
    print("  Step 5: Partial refund of 1")
    partial_refund_current_payment(page, "1")
    print("  Step 6: Verify payment page amount and refund")
    assert_payment_page(page, PAYMENT_NAME, "$5.00", "-$1.00")
    print("  Back-office partial refund verified")
