"""Client-portal checkout flow for offset_fees.

Opens the client portal with the client's JWT (vitrage `cp_iframe`), pays the
past appointment with the saved card, and asserts the offset-fee badge, the
checkout summary fee row, the processing-fee line, and the payment success
page. Mirrors the legacy CPScheduler / CPPaymentForm / CPPaymentDialog /
PaymentConfirmation chain.
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page

from tests.payments.offset_fees.offset_fees_ui import FAST_UI_TIMEOUT, first_visible

CP_READY = ".quick-actions, .matter-picker"
BOOKINGS_MENU = '[data-qa="client-area-menu-bookings"]'
BOOKING_TITLE = ".booking-title"
PAST_TAB = '[data-qa="tab-selector-past"]'
BOOKING_ITEM = ".booking-list-item.list-item"
BOOKING_PAGE = ".booking-page"
MEETING_ACTION = ".action.v-btn .v-btn__content"
PAY_BUTTON = "button[data-qa='payButton'], button.checkout-btn"
CHECKOUT_DIALOG = ".checkout-dialog"
SELECTED_CARD_FEE_BADGE = ".payment-method-card.selected .payment-method-card__fee-badge"
CHECKOUT_SUMMARY = ".summary"
PROCEED_TO_PAYMENT = '[data-qa="perform-payment-action"]'
SUCCESS_PAGE = ".done-loading[data-qa='payment-success-page']"
SUCCESS_TITLE = "span.briliant"
SUCCESS_AMOUNT = "span.paymet-text"


def vitrage_base(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if "app.meet2know.com" in base:
        return "https://live.meet2know.com"
    if "app.vcita.com" in base:
        return "https://live.vcita.com"
    if "app-" in base and ".external.int-eks.vchost.co" in base:
        return base.replace("https://app-", "https://vitrage-", 1)
    raise ValueError(f"Cannot derive vitrage base URL from base_url={base!r}")


def open_client_portal(page: Page, context: dict):
    """Navigate to the client portal with the client JWT and return the CP frame."""
    client = context["offset_client"]
    pivot_uid = context["auto_account"]["pivot_uid"]
    url = f"{vitrage_base(context)}/site/{pivot_uid}/action?client_jwt={client['token']}"
    page.goto(url, wait_until="domcontentloaded")
    frame = _wait_cp_frame(page)
    if frame is None:
        raise AssertionError("Client portal frame (cp_iframe) did not become ready")
    return frame


def open_past_meeting_payment(page: Page, context: dict) -> None:
    """Open the past appointment, choose Pay, and open the checkout dialog."""
    frame = _cp_frame(page)
    frame.locator(BOOKINGS_MENU).first.click(timeout=FAST_UI_TIMEOUT)
    frame.locator(PAST_TAB).first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    frame.locator(PAST_TAB).first.click(timeout=FAST_UI_TIMEOUT)

    meeting_name = context["offset_service_name"]
    item = _booking_item_by_title(page, meeting_name)
    if item is None:
        raise AssertionError(f"Past booking '{meeting_name}' did not appear in the bookings list")
    item.click(timeout=FAST_UI_TIMEOUT)

    frame = _cp_frame(page)
    frame.locator(BOOKING_PAGE).first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    pay_action = _meeting_action(page, "Pay")
    if pay_action is None:
        raise AssertionError("Pay action was not available on the meeting page")
    pay_action.click(timeout=FAST_UI_TIMEOUT)

    _ensure_checkout_open(page)


def assert_fee_badge(page: Page, expected: str) -> None:
    badge = _checkout_locator(page, SELECTED_CARD_FEE_BADGE)
    if badge is None:
        raise AssertionError("Selected card fee badge did not appear in checkout")
    actual = badge.inner_text(timeout=FAST_UI_TIMEOUT)
    assert _normalize(actual) == _normalize(expected), (
        f"Fee badge mismatch: expected '{expected}', got '{actual}'"
    )


def assert_summary_fee_row(page: Page, label: str, amount: str) -> None:
    summary = _checkout_locator(page, CHECKOUT_SUMMARY)
    if summary is None:
        raise AssertionError("Checkout summary did not appear")
    text = re.sub(r"\s+", " ", summary.inner_text(timeout=FAST_UI_TIMEOUT)).strip()
    assert label.lower() in text.lower(), f"Summary missing fee label '{label}': {text}"
    assert amount in text, f"Summary missing fee amount '{amount}': {text}"


def assert_processing_fee_line(page: Page) -> None:
    summary = _checkout_locator(page, CHECKOUT_SUMMARY)
    if summary is None:
        raise AssertionError("Checkout summary did not appear")
    text = summary.inner_text(timeout=FAST_UI_TIMEOUT)
    assert re.search(r"surcharge|convenience", text, re.I), (
        f"Checkout summary did not show a processing (offset) fee line: {text}"
    )


def proceed_and_assert_success(page: Page, amount_received: str) -> None:
    proceed = _checkout_locator(page, PROCEED_TO_PAYMENT)
    if proceed is None:
        raise AssertionError("Proceed-to-payment action did not appear")
    proceed.click(timeout=FAST_UI_TIMEOUT)

    success = _wait_in_cp(page, SUCCESS_PAGE, timeout=FAST_UI_TIMEOUT * 2)
    if success is None:
        raise AssertionError("Payment success page did not display")
    title = _cp_frame(page).locator(SUCCESS_TITLE).first.inner_text(timeout=FAST_UI_TIMEOUT)
    assert "payment confirmed" in title.lower(), f"Unexpected success title: {title}"
    amount_text = _cp_frame(page).locator(SUCCESS_AMOUNT).first.inner_text(timeout=FAST_UI_TIMEOUT)
    assert amount_received in amount_text, (
        f"Success amount mismatch: expected '{amount_received}' in '{amount_text}'"
    )


def _cp_frame(page: Page):
    frame = page.frame(name="cp_iframe")
    return frame if frame is not None else _wait_cp_frame(page)


def _wait_cp_frame(page: Page, timeout: int = FAST_UI_TIMEOUT * 2):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        frame = page.frame(name="cp_iframe")
        if frame is not None:
            try:
                if frame.locator(CP_READY).count() > 0:
                    return frame
            except Exception:
                pass
        for candidate in page.frames:
            try:
                if candidate.locator(CP_READY).count() > 0:
                    return candidate
            except Exception:
                continue
        time.sleep(0.2)
    return None


def _booking_item_by_title(page: Page, title: str, timeout: int = FAST_UI_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        frame = _cp_frame(page)
        items = frame.locator(BOOKING_ITEM)
        for index in range(items.count()):
            item = items.nth(index)
            try:
                if title in (item.locator(BOOKING_TITLE).first.inner_text(timeout=1000) or ""):
                    return item
            except Exception:
                continue
        time.sleep(0.2)
    return None


def _meeting_action(page: Page, action: str, timeout: int = FAST_UI_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        frame = _cp_frame(page)
        actions = frame.locator(MEETING_ACTION)
        for index in range(actions.count()):
            candidate = actions.nth(index)
            try:
                if action.lower() in (candidate.inner_text(timeout=1000) or "").lower():
                    return candidate
            except Exception:
                continue
        time.sleep(0.2)
    return None


def _ensure_checkout_open(page: Page) -> None:
    """Bring up the checkout dialog after choosing Pay on the meeting.

    The redesigned client-portal checkout opens the dialog directly from the
    meeting's Pay action. Older flows surface an intermediate Pay button first;
    only press it when the checkout summary/proceed action is not already shown.
    """
    if _wait_in_cp(page, f"{PROCEED_TO_PAYMENT}, {CHECKOUT_DIALOG}", timeout=FAST_UI_TIMEOUT) is not None:
        return
    pay = _wait_in_cp(page, PAY_BUTTON, timeout=FAST_UI_TIMEOUT)
    if pay is None:
        raise AssertionError("Neither the checkout dialog nor an intermediate Pay button appeared")
    pay.scroll_into_view_if_needed(timeout=FAST_UI_TIMEOUT)
    pay.evaluate("(el) => el.click()")
    if _wait_in_cp(page, f"{PROCEED_TO_PAYMENT}, {CHECKOUT_DIALOG}", timeout=FAST_UI_TIMEOUT) is None:
        raise AssertionError("Checkout dialog did not open after pressing Pay")


def _checkout_locator(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    return _wait_in_cp(page, selector, timeout=timeout)


def _wait_in_cp(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        frame = _cp_frame(page)
        if frame is not None:
            found = first_visible([frame.locator(selector)], timeout=300)
            if found is not None:
                return found
        time.sleep(0.1)
    return None


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text or "")
