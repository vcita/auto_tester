"""UI flow for sending a card-on-file request from a client's payment methods.

Mirrors the legacy `sendCardOnFileRequest` / `getCardOnFileRequest` flow. The
client page nests iframes (POV > Angular > Vue); the Payments tab, the add-card
empty-state CTA, the add-payment-method dialog (with its "Request card" segment,
defaulting to the client's email), and the resulting "Card request sent on …"
label all live in the inner Vue iframe, so controls are resolved across the page
and all frames.

All explicit waits are capped at 5s per the autotester wait policy, except the
client-page load budget (a page-readiness allowance, like login waiting for the
dashboard, not an element wait).
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

FAST_UI_TIMEOUT = 5000
CLIENT_PAGE_LOAD_TIMEOUT = 15000

PAYMENTS_TAB = 'div.v-tab:has-text("Payments")'
ADD_CARD_EMPTY_STATE = "div.empty-state-cta.empty-state-content"
ADD_CARD_DIALOG = '[data-qa="add-payment-method-dialog"]'
REQUEST_SEGMENT = '[data-qa="VcSegmentedControl-item-1"]'
SEND_REQUEST_BUTTON = '[data-qa="vc-footer-Send request"]'
CARD_REQUEST_TEXT = ".card-request__description > div"


def _find_control(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    """Return the first visible match for `selector` across the page and all frames."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            try:
                locator = scope.locator(selector)
                for index in range(locator.count()):
                    candidate = locator.nth(index)
                    if candidate.is_visible():
                        return candidate
            except Exception:
                continue
        time.sleep(0.1)
    return None


def _open_client_payments_tab(page: Page, context: dict, client_id: str) -> None:
    base = (context.get("base_url") or "").rstrip("/")
    page.goto(f"{base}/app/clients/{client_id}", wait_until="domcontentloaded")
    payments_tab = _find_control(page, PAYMENTS_TAB, timeout=CLIENT_PAGE_LOAD_TIMEOUT)
    if payments_tab is None:
        raise AssertionError("Payments tab did not appear on the client page")
    payments_tab.click(timeout=FAST_UI_TIMEOUT)


def send_card_on_file_request(page: Page, context: dict, client_id: str) -> None:
    """Open the client's payment methods and send a card-on-file request by email.

    The redesigned dialog defaults to the "Request card" segment's email channel
    pre-filled with the client's email, so the request is sent by confirming it.
    """
    _open_client_payments_tab(page, context, client_id)

    open_cta = _find_control(page, ADD_CARD_EMPTY_STATE, timeout=FAST_UI_TIMEOUT)
    if open_cta is None:
        raise AssertionError("Add-card empty-state CTA did not appear on the client page")
    open_cta.click(timeout=FAST_UI_TIMEOUT)

    if _find_control(page, ADD_CARD_DIALOG, timeout=FAST_UI_TIMEOUT) is None:
        raise AssertionError("Add payment method dialog did not open")

    segment = _find_control(page, REQUEST_SEGMENT, timeout=FAST_UI_TIMEOUT)
    if segment is None:
        raise AssertionError("'Request card' segment did not appear in the dialog")
    segment.click(timeout=FAST_UI_TIMEOUT)

    send_button = _find_control(page, SEND_REQUEST_BUTTON, timeout=FAST_UI_TIMEOUT)
    if send_button is None:
        raise AssertionError("'Send request' button did not appear in the dialog")
    send_button.click(timeout=FAST_UI_TIMEOUT)


def read_card_request_text(page: Page) -> str:
    """Return the 'Card request sent on …' label that replaces the empty state.

    Its appearance is the readiness signal that the request was sent (the dialog
    closes and the payment-methods box re-renders the pending request).
    """
    label = _find_control(page, CARD_REQUEST_TEXT, timeout=FAST_UI_TIMEOUT)
    if label is None:
        raise AssertionError("Card-on-file request label did not appear after sending the request")
    return (label.inner_text() or "").strip()
