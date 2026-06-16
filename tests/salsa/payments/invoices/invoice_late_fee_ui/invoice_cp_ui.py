"""Client-portal invoice viewing for the invoice_late_fee_ui subcategory.

Migrated from automation-js:
  pages/desktop/ClientPortal/dashboard.js       (OpenPaymentsListPage)
  pages/desktop/ClientPortal/Payments/paymentsList.js (openListItem -> pending tab)
  pages/desktop/ClientPortal/invoice.js         (CPsInvoicePage.getCPInvoiceData)

Opens the client portal as the client (via client_jwt, fresh context) — reusing the
proven open-portal pattern from coupons_checkout — navigates Payments -> Pending, opens
the invoice payment request, and asserts the CP invoice page (name, client, price, and
the "Late fees" caption).
"""

import time

from playwright.sync_api import Page

from tests.salsa.sales.estimates.estimates_helpers import CP_VITRAGE, pivot_uid

NAV_TIMEOUT = 20000  # CP (re)navigation / list render readiness
UI_TIMEOUT = 5000

CP_IFRAME = "#cp_iframe"
PAYMENTS_MENU = "[data-qa='client-area-menu-payments']"
PENDING_TAB = '[data-qa="tab-selector-pending"]'
PAYMENT_TITLE = "span.payment-title"
INVOICE_PAGE = ".payment-entity-page"
LATE_FEE_TITLE = ".late-fee-title"


def open_portal(page: Page, context: dict, portal_token: str):
    """Open a fresh client-portal browser context for the client. Returns (cp_page, cp_context)."""
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    cp_page = cp_context.new_page()
    url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/action?client_jwt={portal_token}"
    cp_page.goto(url, wait_until="domcontentloaded")
    return cp_page, cp_context


def open_pending_invoice(cp_page: Page, invoice_name: str) -> None:
    """Payments menu -> Pending tab -> open the invoice payment request by name."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)

    payments = cp_frame.locator(PAYMENTS_MENU).first
    payments.wait_for(state="visible", timeout=NAV_TIMEOUT)
    payments.click()

    pending = cp_frame.locator(PENDING_TAB).first
    pending.wait_for(state="visible", timeout=NAV_TIMEOUT)
    pending.click()

    item = cp_frame.locator(PAYMENT_TITLE, has_text=invoice_name).first
    item.wait_for(state="visible", timeout=NAV_TIMEOUT)
    item.click()

    cp_frame.locator(INVOICE_PAGE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)


def assert_cp_invoice(cp_page: Page, *, invoice_name: str, client: str, price: str,
                      late_fee: str) -> None:
    """Assert the CP invoice page shows the name, client, price, and late-fee caption.

    Polls the entity page body (it renders asynchronously after the list click), mirroring
    the assert_cp_estimate pattern."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    body = cp_frame.locator("body").first

    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    text = ""
    while time.monotonic() < deadline:
        try:
            text = body.inner_text(timeout=UI_TIMEOUT)
        except Exception:
            text = ""
        if invoice_name in text and client in text and price in text:
            break
        cp_page.wait_for_timeout(500)

    for token in (invoice_name, client, price):
        if token not in text:
            raise AssertionError(f"CP invoice page missing {token!r}")

    # The late-fee caption renders in its own element; confirm both the element and text.
    late_fee_el = cp_frame.locator(LATE_FEE_TITLE).first
    late_fee_el.wait_for(state="visible", timeout=UI_TIMEOUT)
    actual = (late_fee_el.inner_text(timeout=UI_TIMEOUT) or "").strip()
    if late_fee not in actual and late_fee not in text:
        raise AssertionError(f"CP invoice late-fee caption: expected {late_fee!r}, got {actual!r}")
