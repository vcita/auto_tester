"""Back-office payment verification for the QR Code payment flow.

Reopens the payment from the AngularJS Payments Received list and asserts the
detail header name, amount, payment type, and items, mirroring the legacy
PaymentsReceived / PaymentPage assertions. The Angular billing content renders
inside the `angularjs` iframe; the list cold-loads after a cross-document round
trip, so its readiness gets a page-load budget rather than a 5s element wait.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

FAST_UI_TIMEOUT = 5000
BO_PAGE_LOAD_TIMEOUT = 15000

PAYMENTS_TRANSACTIONS = "/app/payments/transactions"
NAME_FILTER = 'input[name="name_filter"]'
LIST_TITLE = "f-ellipsis-tooltip.payment-title .text"

PAYMENT_NAME = "div.summary-header h3"
PAYMENT_AMOUNT = "div.summary-header h2 span"
PAYMENT_TYPE = "div.entity-summary-row .icon-v + div span.caption.wrap"
PAYMENT_ITEMS = "span.invoice-item-content-title"


def assert_back_office_payment(
    page: Page, context: dict, service_name: str, amount: str, payment_type: str
) -> None:
    """Open the QR payment from Payments Received and verify name, amount, type, items."""
    scope = _open_payment(page, context, service_name)

    expected_name = f"Payment for Sale #1 - {service_name}"
    _expect_text(scope.locator(PAYMENT_NAME).first, expected_name)
    _expect_text(scope.locator(PAYMENT_AMOUNT).first, amount)
    _expect_text(scope.locator(PAYMENT_TYPE).first, payment_type)

    actual_items = [item.strip() for item in scope.locator(PAYMENT_ITEMS).all_inner_texts()]
    assert service_name in actual_items, (
        f"Payment items mismatch: expected '{service_name}' in {actual_items}"
    )


def _billing_scope(page: Page):
    """Angular billing content renders inside the angularjs iframe (or the page itself)."""
    if page.locator(".summary-header, .payment-component").count() > 0:
        return page
    iframe = page.locator('iframe[title="angularjs"]')
    if iframe.count() > 0:
        try:
            iframe.first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
        except Exception:
            pass
        return page.frame_locator('iframe[title="angularjs"]')
    return page


def _open_payment(page: Page, context: dict, service_name: str):
    base = (context.get("base_url") or "").rstrip("/")
    page.goto(f"{base}{PAYMENTS_TRANSACTIONS}", wait_until="domcontentloaded")

    search = _wait_search_input(page)
    if search is None:
        raise AssertionError("Payments Received search did not load")
    search.fill(context["created_client_name"].split(" ")[0], timeout=FAST_UI_TIMEOUT)

    link = _wait_payment_row(page, service_name)
    if link is None:
        raise AssertionError(f"Payment row for '{service_name}' did not appear in Payments Received")
    link.evaluate("(el) => el.click()")
    page.wait_for_url(
        f"**{PAYMENTS_TRANSACTIONS}/**", wait_until="domcontentloaded", timeout=BO_PAGE_LOAD_TIMEOUT
    )
    return _billing_scope(page)


def _wait_search_input(page: Page):
    deadline = time.monotonic() + BO_PAGE_LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        search = _billing_scope(page).locator(NAME_FILTER).first
        try:
            if search.count() > 0 and search.is_visible():
                return search
        except Exception:
            pass
        time.sleep(0.3)
    return None


def _wait_payment_row(page: Page, service_name: str):
    deadline = time.monotonic() + BO_PAGE_LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        scope = _billing_scope(page)
        title = scope.locator(LIST_TITLE).filter(has_text=service_name).first
        try:
            if title.count() > 0 and title.is_visible():
                return title.locator("xpath=ancestor::a[1]").first
        except Exception:
            pass
        time.sleep(0.3)
    return None


def _expect_text(locator, expected: str, timeout: int = FAST_UI_TIMEOUT) -> None:
    deadline = time.monotonic() + timeout / 1000
    last = ""
    while time.monotonic() < deadline:
        try:
            last = locator.inner_text(timeout=1000)
            if expected in last:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise AssertionError(f"Expected text '{expected}' but found '{last}'")
