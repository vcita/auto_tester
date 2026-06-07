"""UI helpers for the product_payments migration (VCITA2-13858).

A product payment request lives on the Product Order page
(``/app/product-order/{id}``), whose detail markup is the sale-style card
(``span.main-title`` / ``span.price`` / ``span.status-text`` / ``span.data-part``)
rather than the booking payment-status card. The take-payment / POS / invoice /
Payments-Received flows are identical to events, so the entity-agnostic helpers
are imported from :mod:`event_payments_helpers` rather than duplicated.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page, Frame

from tests.payments.event_payments.event_payments_helpers import (
    app_base,
    _orders_frame,
    _wizard_frame,
    _fill_money_amount,
    _choose_payment_method,
    search_payments,  # noqa: F401  re-exported for scenario use
    pay_for_invoice,  # noqa: F401  invoice-pay flow is entity-agnostic
    UI_TIMEOUT,
    PAGE_TIMEOUT,
    NAV_TIMEOUT,
    ORDERS_RELOAD_RETRIES,
    TAKE_PAYMENT_BTN,
    RECORD_SECTION_BTN,
    TAKE_PAYMENT_CONFIRM,
    SEND_INVOICE_BTN,
    WIZARD_TITLE,
    FROM_FOLD,
    BILLING_EDIT_BTN,
    BILLING_TEXTAREA,
    INVOICE_SEND_BTN,
)

RECORD_BTN = f"{RECORD_SECTION_BTN}, [data-qa='record']"

# Product Order detail (Angular, sale-style markup - see legacy productOrder.js)
PRODUCT_NAME = "span.main-title"
PRODUCT_PRICE = "span.price"
PRODUCT_STATUS = "span.status-text"
PRODUCT_CLIENT = "span.data-part"

PS_EDIT = "[data-qa='edit_payment_status']"
PS_MORE_ACTIONS = "i[data-qa='more-actions']"
PS_WAIVE = "[data-qa='waive_payment']"
# The product cancel-confirm dialog renders a generic "Submit" button rather than
# the booking-style ng-click="cancel_payment()" button - accept either.
PS_CONFIRM_CANCEL = (
    "button[ng-click='cancel_payment()'], button[data-qa='confirm-action'], "
    "md-dialog button.md-primary, md-dialog button[type='submit']"
)
REFUND_CHECKBOX = 'md-checkbox[ng-model="dialog.issue_refund"]'

# Edit-amount dialog (AddProductDialog, #vue_wizard_iframe)
EDIT_PRICE_INPUT = '[data-qa="product-price"]'
EDIT_SAVE_BTN = 'button[data-qa="vc-footer-Save"]'


def _settle(page: Page) -> None:
    """Best-effort wait for in-flight XHRs (record/cancel/edit POST) to settle,
    replacing fixed post-action sleeps. Bounded by UI_TIMEOUT; never a hard gate
    (callers re-navigate and poll)."""
    try:
        page.wait_for_load_state("networkidle", timeout=UI_TIMEOUT)
    except Exception:
        pass


def _store(context: dict) -> dict:
    return context["product_payments"]


def _order_id(context: dict, product_name: str | None = None) -> str:
    store = _store(context)
    if product_name in (None, "this"):
        order = store["last_order"]
    else:
        order = store["orders"].get(product_name)
        if not order:
            raise AssertionError(f"No product order for '{product_name}' in context")
        store["last_order"] = order
    return order["id"]


def _product_frame(page: Page, timeout_ms: int = NAV_TIMEOUT) -> Frame:
    """Frame hosting the product-order payment card (state / take-payment / actions)."""
    markers = [PRODUCT_STATUS, TAKE_PAYMENT_BTN, PS_MORE_ACTIONS]
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            for marker in markers:
                try:
                    if frame.locator(marker).count() > 0:
                        return frame
                except Exception:
                    continue
        page.wait_for_timeout(300)
    raise AssertionError("Product order payment card did not load")


def open_product_order(page: Page, context: dict,
                       product_name: str | None = None) -> Frame:
    """Open a product order detail page by id and return its payment-card frame."""
    order_id = _order_id(context, product_name)
    page.goto(f"{app_base(context)}/app/product-order/{order_id}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    return _product_frame(page)


def _first_text(frame: Frame, selector: str) -> str:
    loc = frame.locator(selector).first
    loc.wait_for(state="visible", timeout=UI_TIMEOUT)
    return loc.inner_text(timeout=UI_TIMEOUT) or ""


def read_product_order(frame: Frame) -> dict:
    frame.locator(PRODUCT_STATUS).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    return {
        "product_name": _first_text(frame, PRODUCT_NAME).strip(),
        "client_full_name": _first_text(frame, PRODUCT_CLIENT).strip(),
        "amount": " ".join(_first_text(frame, PRODUCT_PRICE).replace("US", "").split()),
        "state": _first_text(frame, PRODUCT_STATUS).replace(":", "").strip(),
    }


def assert_product_payment_request(page: Page, context: dict, expected: dict,
                                   product_name: str | None = None) -> None:
    """Open the product order and assert the payment request matches `expected`.

    The product-order detail lags the API write (paying / cancelling), so
    re-navigate while polling until the expected fields settle."""
    nav = product_name or expected.get("product_name")
    frame = open_product_order(page, context, nav)
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    actual: dict = {}
    while time.monotonic() < deadline:
        actual = read_product_order(frame)
        if all(actual.get(k) == v for k, v in expected.items()):
            return
        time.sleep(1.0)
        frame = open_product_order(page, context, nav)
    mismatch = {k: (v, actual.get(k)) for k, v in expected.items() if actual.get(k) != v}
    raise AssertionError(f"Product payment request mismatch (expected, actual): {mismatch}")


def assert_product_request_via_orders(page: Page, context: dict, expected: dict,
                                      product_name: str) -> None:
    """Open the product order via Billing & Invoicing and assert it matches `expected`.

    Used when the order was created through the UI (so its id is not held in
    context) - the order is reached by its product title through SPA routing."""
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    actual: dict = {}
    while time.monotonic() < deadline:
        frame = _open_product_order_via_orders(page, context, product_name)
        actual = read_product_order(frame)
        if all(actual.get(k) == v for k, v in expected.items()):
            return
        time.sleep(1.0)
    mismatch = {k: (v, actual.get(k)) for k, v in expected.items() if actual.get(k) != v}
    raise AssertionError(f"Product payment request mismatch (expected, actual): {mismatch}")


def edit_product_amount(page: Page, context: dict, amount: str,
                        product_name: str | None = None) -> None:
    """Edit the product payment-request amount via the AddProductDialog wizard."""
    frame = open_product_order(page, context, product_name)
    frame.locator(PS_EDIT).first.click()
    price = _wizard_field(page, EDIT_PRICE_INPUT)
    price.fill(str(amount))
    save_frame = _frame_with_selector(page, EDIT_SAVE_BTN)
    save_frame.locator(EDIT_SAVE_BTN).first.click()
    _settle(page)


def cancel_product_request(page: Page, context: dict, refund: bool = False,
                           product_name: str | None = None) -> None:
    """Waive (cancel) the product payment request, optionally issuing a refund.

    The confirm dialog renders in a separate frame from the product card, so it is
    located by scanning all frames for the Submit / refund controls."""
    frame = open_product_order(page, context, product_name)
    frame.locator(PS_MORE_ACTIONS).first.click()
    waive = frame.locator(PS_WAIVE).first
    waive.wait_for(state="visible", timeout=UI_TIMEOUT)
    waive.click()
    dialog = _confirm_dialog_frame(page)
    if refund:
        check = dialog.locator(REFUND_CHECKBOX).first
        check.wait_for(state="visible", timeout=UI_TIMEOUT)
        check.click()
    confirm = dialog.get_by_role("button", name="Submit").first
    if confirm.count() == 0:
        confirm = dialog.locator(PS_CONFIRM_CANCEL).first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click()
    confirm.wait_for(state="hidden", timeout=NAV_TIMEOUT)
    _settle(page)


def _confirm_dialog_frame(page: Page, timeout_ms: int = NAV_TIMEOUT) -> Frame:
    """Frame hosting the cancel-payment confirm dialog (Submit button)."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.get_by_role("button", name="Submit").count() > 0:
                    return frame
                if frame.locator(PS_CONFIRM_CANCEL).count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError("Cancel-payment confirm dialog did not load")


def _record_cash_payment(page: Page, amount: str) -> None:
    """Drive the product Take Payment dialog (Record payment -> Cash -> confirm).

    The product-order take-payment modal renders in a different frame than the
    take-payment button, so the dialog frame is located by scanning all frames for
    the record-payment action."""
    dialog = _frame_with_selector(page, RECORD_BTN)
    record = dialog.locator(RECORD_BTN).first
    record.wait_for(state="visible", timeout=NAV_TIMEOUT)
    record.click()
    _fill_money_amount(dialog, amount)
    _choose_payment_method(dialog, "Cash")
    overlay = dialog.locator("div.md-select-menu-container.md-active")
    if overlay.count() > 0:
        overlay.first.wait_for(state="hidden", timeout=UI_TIMEOUT)
    confirm = dialog.locator(TAKE_PAYMENT_CONFIRM).first
    confirm.wait_for(state="visible", timeout=NAV_TIMEOUT)
    confirm.click()
    confirm.wait_for(state="hidden", timeout=NAV_TIMEOUT)


def pay_for_product(page: Page, context: dict, amount: str,
                    product_name: str | None = None) -> None:
    """Record a Cash payment against the product payment request (POS denied)."""
    frame = open_product_order(page, context, product_name)
    frame.locator(TAKE_PAYMENT_BTN).first.click()
    _record_cash_payment(page, amount)
    # The record POST settles asynchronously; wait for network idle (not a fixed
    # sleep) before the caller navigates away.
    _settle(page)


def record_product_via_pos(page: Page, context: dict,
                           product_name: str | None = None) -> None:
    """Record the product payment through Point of Sale (POS enabled)."""
    from tests.payments.deposits.deposits_invoice_ui import (
        FAST_UI_TIMEOUT, LOAD_TIMEOUT, _find_control, _require,
    )
    from tests.payments.event_payments.event_payments_helpers import (
        POS_CHECKOUT_ACTIVATOR, POS_CHECKOUT_RECORD, POS_TAKE_PAYMENT_DIALOG,
        POS_METHOD_SELECT, POS_METHOD_OPTION, TAKE_PAYMENT_CONFIRM,
    )
    frame = open_product_order(page, context, product_name)
    frame.locator(TAKE_PAYMENT_BTN).first.click()
    _require(page, POS_CHECKOUT_ACTIVATOR, "POS checkout activator", timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_CHECKOUT_RECORD, "POS record-payment action").click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_TAKE_PAYMENT_DIALOG, "Take payment dialog", timeout=LOAD_TIMEOUT)
    _require(page, POS_METHOD_SELECT, "Record method picker").click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_METHOD_OPTION, "Cash record option").click(timeout=FAST_UI_TIMEOUT)
    _require(page, TAKE_PAYMENT_CONFIRM, "Take payment confirm").click(timeout=FAST_UI_TIMEOUT)
    deadline = time.monotonic() + LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _find_control(page, POS_TAKE_PAYMENT_DIALOG, timeout=300) is None:
            return
        time.sleep(0.2)
    raise AssertionError("Take payment dialog did not close after recording the product sale")


def _open_product_order_via_orders(page: Page, context: dict, product_name: str) -> Frame:
    """Reach the product order via Billing & Invoicing SPA routing.

    The "Create invoice" button only mounts the POV invoice wizard when the
    product order is entered via in-app SPA navigation (a direct deep-link loads
    the page without the wizard host, so the click is a silent no-op). Navigating
    from the Orders list and clicking the row performs that SPA navigation."""
    for _ in range(ORDERS_RELOAD_RETRIES + 1):
        page.goto(f"{app_base(context)}/app/payments/orders",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        _, row = _orders_frame(page, product_name)
        if row is not None:
            row.click()
            return _product_frame(page)
        page.wait_for_timeout(1500)
    raise AssertionError(f"Order row for '{product_name}' not found in Billing & Invoicing")


def invoice_product(page: Page, context: dict, invoice_name: str,
                    billing_address: str, product_name: str | None = None) -> None:
    """Create an invoice from the product payment request (POV-routed)."""
    title_name = product_name or _store(context)["last_order"]["product_name"]
    frame = _open_product_order_via_orders(page, context, title_name)
    frame.locator(SEND_INVOICE_BTN).first.click()
    wizard = _wizard_frame(page)
    title = wizard.locator(f"{WIZARD_TITLE} input").first
    if title.count() == 0:
        title = wizard.locator(WIZARD_TITLE).first
    title.wait_for(state="visible", timeout=NAV_TIMEOUT)
    title.fill(invoice_name)
    wizard.locator(FROM_FOLD).first.click()
    edit = wizard.locator(BILLING_EDIT_BTN).first
    edit.wait_for(state="visible", timeout=UI_TIMEOUT)
    edit.click()
    textarea = wizard.locator(BILLING_TEXTAREA).first
    textarea.wait_for(state="visible", timeout=UI_TIMEOUT)
    textarea.fill(billing_address)
    wizard.locator(FROM_FOLD).first.click()
    wizard.locator(INVOICE_SEND_BTN).first.click()
    page.wait_for_url("**/app/invoices/**", timeout=NAV_TIMEOUT, wait_until="domcontentloaded")


# Billing & Invoicing order-type filter (mirrors legacy filterByPaymentType)
ORDER_TYPE_FILTER = '[name="type_filter"]'
ORDER_TYPES = ("bookings", "invoices", "packages", "products")


def assert_order_listed(page: Page, context: dict, title: str,
                        order_type: str = "products") -> None:
    """Filter Billing & Invoicing by order type and assert the order titled `title`
    is listed, mirroring legacy `search orders | filter | products` (filterOrders
    selects only the products type before checking the result)."""
    from tests.payments.event_payments.event_payments_helpers import PAYMENT_ROW
    last_error = None
    for _ in range(ORDERS_RELOAD_RETRIES + 1):
        page.goto(f"{app_base(context)}/app/payments/orders",
                  wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        frame = _frame_with_selector(page, ORDER_TYPE_FILTER)
        _apply_type_filter(page, frame, order_type)
        rows = frame.locator(PAYMENT_ROW).filter(has_text=title)
        deadline = time.monotonic() + UI_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if rows.count() > 0 and rows.first.is_visible():
                return
            page.wait_for_timeout(300)
        last_error = f"order '{title}' not visible under '{order_type}' filter"
        page.wait_for_timeout(1000)
    raise AssertionError(f"Order listing assertion failed: {last_error}")


def _apply_type_filter(page: Page, frame: Frame, order_type: str) -> None:
    """Select only `order_type` in the order type_filter (clear the other types)."""
    dropdown = frame.locator(ORDER_TYPE_FILTER).first
    dropdown.wait_for(state="visible", timeout=UI_TIMEOUT)
    dropdown.click()
    target = frame.locator(f'[name="{order_type}"]').first
    target.wait_for(state="visible", timeout=UI_TIMEOUT)
    for other in ORDER_TYPES:
        if other == order_type:
            continue
        opt = frame.locator(f'[name="{other}"]').first
        try:
            if opt.count() > 0 and opt.get_attribute("selected") is not None:
                opt.click()
        except Exception:
            continue
    if target.get_attribute("selected") is None:
        target.click()
    page.keyboard.press("Escape")


def _frame_with_selector(page: Page, selector: str, timeout_ms: int = NAV_TIMEOUT) -> Frame:
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(selector).count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError(f"No frame contained selector {selector!r}")


def _wizard_field(page: Page, selector: str):
    frame = _frame_with_selector(page, selector)
    field = frame.locator(selector).first
    field.wait_for(state="visible", timeout=UI_TIMEOUT)
    return field


# --------------------------------------------------------------------------- #
# Scenario 1 - create & search product (products settings page)
# --------------------------------------------------------------------------- #
ADD_PRODUCT_BTN = "[data-qa='action-button-products-settings-add']"
DIALOG_NAME = "[data-qa='product-name']"
DIALOG_DESCRIPTION = "[data-qa='product-description']"
DIALOG_PRICE = "[data-qa='product-price']"
DIALOG_COST = "[data-qa='product-cost']"
DIALOG_SKU = "[data-qa='product-sku']"
DIALOG_TAX_PICKER = ".tax-picker"
DIALOG_SAVE = "[data-qa='modern-product-dialog'] [data-qa='vc-footer-Save']"


def _tax_option(name: str, rate: str) -> str:
    """Tax-picker checkbox selector, shared by the create and assign dialogs."""
    return f'[data-qa="tax-{name}-{rate}"]'


PRODUCTS_LIST_READY = "[data-qa='filter-search']"


def _open_product_dialog(page: Page) -> Frame:
    """Click "Add Product" and return the dialog frame.

    The Angular "Add Product" button posts a message to the Vue iframe to mount
    the dialog; if the Vue list is not ready yet the message is dropped, so wait
    for list readiness and re-click until the dialog appears."""
    _frame_with_selector(page, PRODUCTS_LIST_READY)
    for _ in range(3):
        _js_click(_visible_in_frames(page, ADD_PRODUCT_BTN))
        try:
            return _frame_with_selector(page, DIALOG_NAME, timeout_ms=5000)
        except AssertionError:
            page.wait_for_timeout(1000)
    raise AssertionError("Add product dialog did not open after clicking Add Product")


def create_product_ui(page: Page, context: dict, *, name: str, description: str,
                      price: str, cost: str | None = None, sku: str | None = None,
                      taxes: list[dict] | None = None) -> None:
    """Create a product through the Add product dialog (mirrors legacy createProduct)."""
    from tests.products.products_helpers import open_products_page

    open_products_page(page, context)
    frame = _open_product_dialog(page)
    frame.locator(DIALOG_NAME).first.fill(name)
    if description:
        frame.locator(DIALOG_DESCRIPTION).first.fill(description)
    frame.locator(DIALOG_PRICE).first.fill(str(price))
    if cost:
        frame.locator(DIALOG_COST).first.fill(str(cost))
    if sku:
        frame.locator(DIALOG_SKU).first.fill(str(sku))
    if taxes:
        frame.locator(DIALOG_TAX_PICKER).first.click()
        for tax in taxes:
            option = frame.locator(_tax_option(tax["name"], tax["rate"])).first
            option.wait_for(state="visible", timeout=UI_TIMEOUT)
            if not option.is_checked():
                _js_click(option)
        # Collapse the tax dropdown (Escape would close the whole dialog).
        frame.locator(DIALOG_TAX_PICKER).first.click()
        page.wait_for_timeout(300)
    _js_click(frame.locator(DIALOG_SAVE).first)
    _settle(page)


def search_products_ui(page: Page, context: dict, query: str,
                       expected_names: list[str]) -> None:
    """Search the products list and assert the visible names match `expected_names`."""
    from tests.products.products_helpers import open_products_page, search_products

    open_products_page(page, context)
    names = search_products(page, query, expected_names)
    assert names == expected_names, (
        f"Product search for '{query}' returned {names}, expected {expected_names}"
    )


# --------------------------------------------------------------------------- #
# Scenarios 2 & 3 - assign a product to a client via the client card UI
# --------------------------------------------------------------------------- #
TAB_ITEM = "div.v-tab, md-tab-item>span, .v-tabs__item"
ADD_PAYMENT_BTN = ".add-payment-btn-desktop button"
ADD_PAYMENT_PRODUCT = "[data-qa='products']"
PICKER_INPUT = "[data-qa='product-select-input']"
TAX_ENABLE = "[data-qa*='tax_assigned']"
ASSIGN_TAX_PICKER = ".tax-picker"
ASSIGN_ADD_BTN = "button[data-qa='vc-footer-Add']"


def _js_click(locator) -> None:
    """Click via the element's own handler - Angular md-menu / Vue overlays drop
    Playwright's synthetic click, so dispatch the DOM click directly."""
    locator.wait_for(state="visible", timeout=UI_TIMEOUT)
    locator.evaluate("el => el.click()")


def _visible_in_frames(page: Page, selector: str, timeout_ms: int = NAV_TIMEOUT):
    """Return the first *visible* match for `selector` across all frames.

    The Payments tab content and the open add-payment md-menu both expose
    ``[data-qa='products']``; scoping to the visible match avoids clicking the
    hidden tab-content duplicate."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                loc = frame.locator(f"{selector} >> visible=true").first
                if loc.count() > 0:
                    return loc
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError(f"No visible element for selector {selector!r}")


def _click_tab(page: Page, name: str) -> None:
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                tab = frame.locator(TAB_ITEM).filter(has_text=name).first
                if tab.count() > 0:
                    tab.click(timeout=UI_TIMEOUT)
                    return
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError(f"Client-card tab '{name}' not found")


def assign_product_ui(page: Page, context: dict, *, product_name: str,
                      taxes: list[dict] | None = None) -> None:
    """Assign a product to the seeded client through the client card Payments tab
    (mirrors legacy ClientPage.assignProduct -> AddProductDialog.assignProduct)."""
    client = _store(context)["client"]
    page.goto(f"{app_base(context)}/app/clients/{client['id']}",
              wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    _click_tab(page, "Payments")
    add = _frame_with_selector(page, ADD_PAYMENT_BTN)
    add.locator(ADD_PAYMENT_BTN).first.click()
    _js_click(_visible_in_frames(page, ADD_PAYMENT_PRODUCT))

    dlg = _frame_with_selector(page, PICKER_INPUT)
    dlg.locator(PICKER_INPUT).first.click()
    option = dlg.locator(
        f"md-option:has-text('{product_name}'), .v-list-item:has-text('{product_name}'), "
        f"li:has-text('{product_name}')"
    ).first
    _js_click(option)

    if taxes:
        _js_click(dlg.locator(TAX_ENABLE).first)
        dlg.locator(ASSIGN_TAX_PICKER).first.click()
        for tax in taxes:
            opt = dlg.locator(_tax_option(tax["name"], tax["rate"])).first
            opt.wait_for(state="visible", timeout=UI_TIMEOUT)
            if not opt.is_checked():
                _js_click(opt)
        # Collapse the tax dropdown by re-clicking the picker (Escape closes the
        # whole AddProductDialog), so the Add button is reachable.
        dlg.locator(ASSIGN_TAX_PICKER).first.click()
        page.wait_for_timeout(300)

    add_btn = _frame_with_selector(page, ASSIGN_ADD_BTN)
    _js_click(add_btn.locator(ASSIGN_ADD_BTN).first)
    _settle(page)
