"""Shared UI helpers for the cp_payment_actions subcategory (VCITA2-14227).

Migrated from automation-js features/salsa/cp/payment-actions.feature (scenarios 1 & 2).

Three UI surfaces:
- the public client-portal make-payment form (Scenario 1's "grab pay link" + pay), reusing
  the CP pay-popup -> success pattern from coupons_checkout_cp,
- the back-office TakePaymentDialog on a client-package page (Scenario 2's "pay for
  package $100" record payment), and
- the client-portal payments list (Scenario 2's multi-request list + pay-one-item).

Selector policy: data-qa first (payButton, perform-payment, take_payment,
take-payment-confirmation). The CP payments-list rows and the Angular take-payment
money input expose no data-qa, so the stable legacy CSS from the automation-js page
objects is reused and documented. Element waits are capped at 5s; CP (re)navigation and
the external mock-gateway popup use a longer, justified readiness budget.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

from tests.account_api import pivot_uid
from tests.salsa.payments.refunds_credits.partial_refund_helpers import (
    open_payments_received,
)
from tests.salsa.payments.coupons_checkout.coupons_checkout_cp import (
    CHECKOUT_DIALOG,
    CP_IFRAME,
    NAV_TIMEOUT,
    PERFORM_PAYMENT,
    POPUP_TIMEOUT,
    UI_TIMEOUT,
    open_portal,
)
from tests.salsa.sales.estimates.estimates_helpers import CP_VITRAGE

MOCK_SUBMIT = "button[type=submit]"

# --- Public CP make-payment form (Scenario 1) -------------------------------- #
PAY_FORM_EMAIL = 'xpath=//label[contains(.,"Email")]/../input'
PAY_FORM_FIRST_NAME = 'xpath=//label[contains(.,"First Name")]/../input'
PAY_FORM_PAY_BTN = "[data-qa='payButton'], .checkout-btn"

# --- CP payments list (Scenario 2) ------------------------------------------- #
PAYMENTS_MENU = "[data-qa='client-area-menu-payments']"
PAYMENTS_LIST_PAGE = "[class*=payments-list-page]"
PAYMENT_ROW = "[paymentrequeststate]"
ROW_TITLE = "[class=payment-title]"
ROW_PRICE = "[class*='price']"
ROW_SUBTITLE = ".sub-title span.black-text"
ROW_COMMENT = "[class*='comment']"
ROW_CHECKBOX = ".v-input--selection-controls__input"
SELECT_ALL_CHECKBOX = ".header [role='checkbox']"
CHECKOUT_BTN = ".checkout-btn"

# --- Back-office Payments Received search (Scenario 1 assertion) -------------- #
PAYMENTS_SEARCH_INPUT = 'input[name="name_filter"]'
PAYMENT_TITLE_BO = "f-ellipsis-tooltip.payment-title .text"

# --- Back-office client-package take-payment dialog (Scenario 2) -------------- #
TAKE_PAYMENT_BTN = "[data-qa='take_payment']"
RECORD_PAYMENT_SECTION_BTN = "[data-qa='record_payment_button']"
PAYMENT_METHOD_SELECT = "md-select[name='payment_method']"
TAKE_PAYMENT_AMOUNT = "input[name='money_amount']"
AMOUNT_CONTAINER = ".payment-amount-container"
TAKE_PAYMENT_CONFIRM = "[data-qa='take-payment-confirmation'][aria-disabled='false']"


# --------------------------------------------------------------------------- #
# Scenario 1 — public make-payment form -> mock popup -> success
# --------------------------------------------------------------------------- #
def open_payment_form(page: Page, context: dict, *, pay_for: str, amount: str):
    """Open a fresh CP context on the public make-payment form (the legacy 'pay link').

    The legacy 'grab pay link' Link Builder produces exactly this public URL
    (vitrage /site/{uid}/make-payment?title=<pay_for>&amount=<amount>); the editor that
    builds it is heavy and crash-prone in headless (VCITA2-14226), so the deterministic
    URL is used directly (same approach as tips_checkout_cp.open_payment_form).
    Returns (cp_page, cp_context).
    """
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    cp_page = cp_context.new_page()
    url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/make-payment?title={pay_for}&amount={amount}"
    cp_page.goto(url, wait_until="domcontentloaded")
    return cp_page, cp_context


def _submit_mock_popup(cp_page: Page, proceed_locator) -> None:
    """Click the perform-payment control, submit the mock-gateway popup, wait for close."""
    with cp_page.context.expect_page(timeout=POPUP_TIMEOUT) as popup_info:
        proceed_locator.click()
    popup = popup_info.value
    popup.wait_for_load_state("domcontentloaded")
    submit = popup.locator(MOCK_SUBMIT).first
    submit.wait_for(state="visible", timeout=UI_TIMEOUT)
    submit.click()
    try:
        popup.wait_for_event("close", timeout=POPUP_TIMEOUT)
    except Exception:
        pass


def pay_via_payment_form(page: Page, context: dict, *, pay_for: str, amount: str,
                         first_name: str, email: str) -> None:
    """New client pays a service via the public CP make-payment form (no tip, mock gateway)."""
    cp_page, cp_context = open_payment_form(page, context, pay_for=pay_for, amount=amount)
    try:
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        email_input = cp_frame.locator(PAY_FORM_EMAIL).first
        email_input.wait_for(state="visible", timeout=NAV_TIMEOUT)
        email_input.fill(email)
        first_name_input = cp_frame.locator(PAY_FORM_FIRST_NAME).first
        first_name_input.fill(first_name)
        # Blur so Vue commits field validation before the pay button advances.
        first_name_input.press("Tab")

        pay_btn = cp_frame.locator(PAY_FORM_PAY_BTN).first
        dialog = cp_frame.locator(CHECKOUT_DIALOG).first
        pay_btn.wait_for(state="visible", timeout=NAV_TIMEOUT)
        pay_btn.click()
        try:
            dialog.wait_for(state="visible", timeout=NAV_TIMEOUT)
        except Exception:
            pay_btn.click()
            dialog.wait_for(state="visible", timeout=NAV_TIMEOUT)

        proceed = cp_frame.locator(PERFORM_PAYMENT).first
        proceed.wait_for(state="visible", timeout=UI_TIMEOUT)
        _submit_mock_popup(cp_page, proceed)
    finally:
        cp_context.close()


# --------------------------------------------------------------------------- #
# Scenario 1 assertion — back-office Payments Received search
# --------------------------------------------------------------------------- #
def assert_payment_in_search(page: Page, *, first_name: str, expected_substrings: list[str]) -> None:
    """Search Payments Received by first name and assert a title contains all substrings.

    Reuses partial_refund_helpers.open_payments_received for navigation, then searches via
    the legacy name_filter and reads payment titles via the legacy payment-title selector.
    The list is async-propagating after a CP payment, so the read is re-checked (bounded).
    """
    scope = open_payments_received(page)
    search = scope.locator(PAYMENTS_SEARCH_INPUT).first
    search.wait_for(state="visible", timeout=NAV_TIMEOUT)
    search.fill(first_name)

    titles: list[str] = []
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    matched = False
    while time.monotonic() < deadline:
        titles_locator = scope.locator(PAYMENT_TITLE_BO)
        count = titles_locator.count()
        titles = []
        for index in range(count):
            text = (titles_locator.nth(index).inner_text(timeout=UI_TIMEOUT) or "").strip()
            titles.append(text)
            if all(sub in text for sub in expected_substrings):
                matched = True
        if matched:
            return
        time.sleep(0.5)
    raise AssertionError(
        f"No payment matching {expected_substrings} found for '{first_name}'. Titles: {titles}"
    )


# --------------------------------------------------------------------------- #
# Scenario 2 — back-office record payment on a client package
# --------------------------------------------------------------------------- #
def _take_payment_frame(page: Page):
    """Return the Playwright Frame that holds the client-package take_payment control.

    The client-package details card renders inside a same-origin child iframe (not the
    legacy ``vue_iframe_main``), so the frame is resolved by scanning page.frames for the
    take_payment data-qa (eventual mount; bounded above the 5s cap as a page-mount wait).
    """
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(TAKE_PAYMENT_BTN).count() > 0:
                    return frame
            except Exception:
                continue
        time.sleep(0.2)
    raise AssertionError("Client-package take_payment control did not appear in any frame")


def record_package_payment(page: Page, context: dict, *, client_package_id: str,
                           amount: str) -> None:
    """Record a (Cash) payment of ``amount`` on a client-package page (back office).

    Navigate to /app/client-package/{id}, open TakePaymentDialog (take_payment), switch to
    the Record-payment section, fill the money amount, pick Cash, and confirm. Mirrors the
    legacy ClientPackage.payForPackage -> TakePaymentDialog.takePayment(RECORD).
    """
    base = (context.get("base_url") or "").rstrip("/")
    page.goto(f"{base}/app/client-package/{client_package_id}", wait_until="domcontentloaded")

    frame = _take_payment_frame(page)
    take_btn = frame.locator(TAKE_PAYMENT_BTN).first
    take_btn.wait_for(state="visible", timeout=NAV_TIMEOUT)
    take_btn.click()

    # The dialog pre-fills the full balance and hides the money input behind a display box;
    # clicking the amount container reveals the editable money_amount input (legacy mock layer).
    frame.locator(AMOUNT_CONTAINER).first.click()
    money = frame.locator(TAKE_PAYMENT_AMOUNT).first
    money.wait_for(state="visible", timeout=UI_TIMEOUT)
    money.fill(amount)

    # Choose the "Record payment (cash/check/other)" path (legacy record-payment section).
    record_section = frame.locator(RECORD_PAYMENT_SECTION_BTN).first
    record_section.wait_for(state="visible", timeout=UI_TIMEOUT)
    record_section.click()

    # Payment method may default to Cash; select it explicitly when the picker is present.
    if frame.locator(PAYMENT_METHOD_SELECT).count() > 0:
        _pick_md_select(frame, PAYMENT_METHOD_SELECT, "Cash")

    confirm = frame.locator(TAKE_PAYMENT_CONFIRM).first
    confirm.wait_for(state="visible", timeout=NAV_TIMEOUT)
    confirm.click()
    # Success toast is the server-acknowledged signal the record persisted.
    _wait_for_toast(frame)


def _pick_md_select(frame, select_selector: str, option_text: str) -> None:
    """Open an Angular md-select and pick the option by visible text."""
    select = frame.locator(select_selector).first
    select.wait_for(state="visible", timeout=UI_TIMEOUT)
    select.click()
    # md-select renders its options in a body-level overlay (same frame document).
    option = frame.get_by_role("option", name=option_text).first
    try:
        option.wait_for(state="visible", timeout=UI_TIMEOUT)
        option.click()
    except Exception:
        frame.get_by_text(option_text, exact=True).first.click(timeout=UI_TIMEOUT)


def _wait_for_toast(frame) -> None:
    """Best-effort wait for the Angular success toast within the 5s cap."""
    try:
        frame.locator(".md-toast-content, md-toast").first.wait_for(
            state="visible", timeout=UI_TIMEOUT
        )
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# Scenario 2 — CP payments list
# --------------------------------------------------------------------------- #
def open_payments_list(page: Page, context: dict, portal_token: str):
    """Open the client portal as the client and navigate to the payments list.

    Returns (cp_page, cp_context, cp_frame). The list is inside #cp_iframe.
    """
    cp_page, cp_context = open_portal(page, context, portal_token)
    # The /action route mounts #cp_iframe and then renders the menu a beat later; wait for
    # the iframe element to attach before resolving the FrameLocator (avoids a transient
    # "frame not found" on the very first read).
    cp_page.locator(CP_IFRAME).wait_for(state="attached", timeout=NAV_TIMEOUT)
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    goto_payments_list(cp_frame)
    return cp_page, cp_context, cp_frame


def goto_payments_list(cp_frame) -> None:
    """Click the CP payments menu and wait for the payments-list page (with rows) to render.

    Clicking the payments menu reloads the CP iframe, which transiently removes #cp_iframe
    and can surface a "frame not found" mid-wait, so the menu-click -> list-render sequence
    is retried on a bounded budget, re-resolving the frame each pass.
    """
    last_error: Exception | None = None
    for _ in range(3):
        try:
            payments = cp_frame.locator(PAYMENTS_MENU).first
            payments.wait_for(state="visible", timeout=NAV_TIMEOUT)
            payments.click()
            cp_frame.locator(PAYMENTS_LIST_PAGE).first.wait_for(
                state="visible", timeout=NAV_TIMEOUT
            )
            cp_frame.locator(PAYMENT_ROW).first.wait_for(state="visible", timeout=UI_TIMEOUT)
            return
        except Exception as error:
            last_error = error
            time.sleep(1)
    raise AssertionError(f"CP payments list did not render after 3 attempts: {last_error}")


def reopen_payments_list(cp_page: Page, context: dict, portal_token: str):
    """Re-open the client portal and navigate to the payments list (returns a fresh cp_frame).

    Paying an item from the list lands on the standalone make-payment success page (no
    sidebar), so the portal is re-opened (legacy re-runs OpenPaymentsListPage) to read the
    updated list rather than trying to navigate out of the success page.
    """
    url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/action?client_jwt={portal_token}"
    cp_page.goto(url, wait_until="domcontentloaded")
    cp_page.locator(CP_IFRAME).wait_for(state="attached", timeout=NAV_TIMEOUT)
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    goto_payments_list(cp_frame)
    return cp_frame


def read_payments_rows(cp_frame) -> list[dict]:
    """Read the CP payments-list rows into [{item_name, price, sub_title_type, comment}]."""
    rows_locator = cp_frame.locator(PAYMENT_ROW)
    count = rows_locator.count()
    rows: list[dict] = []
    for index in range(count):
        row = rows_locator.nth(index)
        item_name = (row.locator(ROW_TITLE).first.inner_text(timeout=UI_TIMEOUT) or "").strip()
        price = (row.locator(ROW_PRICE).first.inner_text(timeout=UI_TIMEOUT) or "").strip()
        sub_title = ""
        sub_locator = row.locator(ROW_SUBTITLE)
        if sub_locator.count() > 0:
            sub_title = (sub_locator.first.inner_text(timeout=UI_TIMEOUT) or "").strip()
        comment = ""
        comment_locator = row.locator(ROW_COMMENT)
        if comment_locator.count() > 0:
            comment = (comment_locator.first.inner_text(timeout=UI_TIMEOUT) or "").strip()
        rows.append({"item_name": item_name, "price": price,
                     "sub_title_type": sub_title, "comment": comment})
    return rows


def wait_for_payments_rows(cp_frame, expected_count: int, *, retries: int = 2) -> list[dict]:
    """Read the payments-list rows, re-reading up to ``retries`` times until the expected
    row count appears (async-propagating list; bounded re-check per the read policy).

    The CP list re-renders its rows just after the page appears, so the #cp_iframe can
    transiently detach mid-read; a transient frame error is treated like a count mismatch
    and re-read on the same bounded budget.
    """
    def _safe_read() -> list[dict] | None:
        try:
            return read_payments_rows(cp_frame)
        except Exception:
            return None

    rows = _safe_read()
    attempt = 0
    while (rows is None or len(rows) != expected_count) and attempt < retries:
        attempt += 1
        time.sleep(1)
        rows = _safe_read()
    if rows is None:
        rows = []
    return rows


def assert_rows(cp_frame, expected: list[dict]) -> None:
    """Assert the CP payments-list rows match ``expected`` (order-sensitive).

    Each expected dict: {item_name, price, sub_title_type, comment(optional)}. Price is
    matched by substring (e.g. "$10.00") so currency/formatting around it is tolerated.
    """
    rows = wait_for_payments_rows(cp_frame, len(expected))
    if len(rows) != len(expected):
        raise AssertionError(
            f"CP payments list row count: expected {len(expected)}, got {len(rows)}: {rows}"
        )
    for index, want in enumerate(expected):
        got = rows[index]
        if want["item_name"] != got["item_name"]:
            raise AssertionError(
                f"Row {index} item_name: expected {want['item_name']!r}, got {got['item_name']!r}"
            )
        if want["price"] not in got["price"]:
            raise AssertionError(
                f"Row {index} ({got['item_name']}) price: expected to contain "
                f"{want['price']!r}, got {got['price']!r}"
            )
        if want.get("sub_title_type") and want["sub_title_type"] != got["sub_title_type"]:
            raise AssertionError(
                f"Row {index} ({got['item_name']}) sub_title_type: expected "
                f"{want['sub_title_type']!r}, got {got['sub_title_type']!r}"
            )
        if want.get("comment") and want["comment"] not in got["comment"]:
            raise AssertionError(
                f"Row {index} ({got['item_name']}) comment: expected to contain "
                f"{want['comment']!r}, got {got['comment']!r}"
            )


ROW_CHECKBOX_INPUT = "input[role='checkbox']"


def _set_row_checked(row, *, checked: bool) -> bool:
    """Set a payments-list row's checkbox to ``checked`` if it is enabled and not already so.

    Returns False if the row's checkbox is disabled (e.g. an invoice that cannot be batch-paid);
    True otherwise. Clicks the styled selection-control wrapper (the input itself is overlaid).
    """
    box = row.locator(ROW_CHECKBOX_INPUT).first
    if box.count() == 0:
        return False
    if box.get_attribute("disabled") is not None:
        return False
    is_checked = box.get_attribute("aria-checked") == "true"
    if is_checked != checked:
        row.locator(ROW_CHECKBOX).first.click()
    return True


def pay_one_item(cp_page: Page, cp_frame, item_name: str) -> None:
    """Pay a single payments-list item by name via the mock gateway.

    The list defaults to all (enabled) rows selected, so check only the target row and
    uncheck every other enabled row, then checkout -> proceed -> mock popup. Mirrors legacy
    payForOneItem + CPPaymentDialog.fillCheckout + Gateways.makePayment.
    """
    rows_locator = cp_frame.locator(PAYMENT_ROW)
    count = rows_locator.count()
    for index in range(count):
        row = rows_locator.nth(index)
        title = (row.locator(ROW_TITLE).first.inner_text(timeout=UI_TIMEOUT) or "").strip()
        _set_row_checked(row, checked=(title == item_name))

    checkout = cp_frame.locator(CHECKOUT_BTN).first
    checkout.wait_for(state="visible", timeout=UI_TIMEOUT)
    checkout.click()

    # The checkout dialog mounts its perform-payment control a beat after the dialog
    # container becomes visible, so wait for the action itself (not just the container).
    cp_frame.locator(CHECKOUT_DIALOG).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    proceed = cp_frame.locator(PERFORM_PAYMENT).first
    proceed.wait_for(state="visible", timeout=NAV_TIMEOUT)
    _submit_mock_popup(cp_page, proceed)
