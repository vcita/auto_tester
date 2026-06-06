"""Helpers for the QR-code payment scenario (migrated from automation-js).

Covers the back-office POS "grab a QR-code payment link" flow (Quick Actions ->
Point of sale -> client picker -> add the paid service -> checkout -> Pay with QR
code -> read the link), paying that link through the public client-portal page in a
separate browser tab via the mock-gateway popup, the back-office QR dialog success,
and the Payments-Received payment-page reader.

Reuse (see prefer-data-qa-selectors / migrate skill): the mock-gateway connection
(`tips_gateway.connect_mock_gateway`), the POS Quick Actions primitives
(`deposits_invoice_ui` / `deposits_pos_ui`), the Payments-Received navigation and
billing-iframe scope (`partial_refund_helpers`), and the CP live-site base
(`estimates_helpers.NAV_TIMEOUT`).

Selector policy: data-qa first. The QR dialog link container (`.payment-content`),
the client-portal link page (`.continue-btn`), the mock popup (`button[type=submit]`),
and the back-office payment-page summary rows have no full data-qa coverage yet, so
the legacy stable selectors are reused; those should gain data-qa in product code.

Waits: element/dialog/state waits are capped at 5s (FAST_UI_TIMEOUT). NAV_TIMEOUT
(portal/app navigation) and PAYMENT_PROPAGATE_TIMEOUT (external mock-gateway popup
round-trip + payment propagation to the back office) are the only longer, justified
eventual-consistency budgets; retries are capped at 2.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page, expect

from tests.payments.deposits.deposits_invoice_ui import (
    FAST_UI_TIMEOUT,
    LOAD_TIMEOUT,
    QUICK_ACTIONS_BUTTON,
    _find_control,
    _require,
    _select_client,
)
from tests.payments.deposits.deposits_pos_ui import TAKE_PAYMENT_ITEM
from tests.payments.refunds_credits.partial_refund_helpers import open_payment_by_name
from tests.sales.estimates.estimates_helpers import NAV_TIMEOUT

PAYMENT_PROPAGATE_TIMEOUT = 20000  # external mock-gateway round-trip + BO propagation

# POS catalog + checkout (POV top-level)
SERVICES_TAB_PANEL = '[data-qa="VcTabs-tab-content-0"]'
CATALOG_ITEM = lambda name: f'[data-qa="catalog-item-{name}"]'  # noqa: E731
ADD_ITEM = '[data-qa="add-item"]'
CHECKOUT_ACTIVATOR = '[data-qa="checkout-actions-activator"]'
CHECKOUT_ACTION_QR = '[data-qa="checkout-action-qr"]'

# QR dialog (POV top-level)
QR_LINK_CONTAINER = ".payment-content[data-link], .payment-content[data-link='']"
QR_LINK_ANY = "[data-link]"
QR_PAYMENT_RECEIVED = "[data-qa='payment-received']"
QR_DONE_BUTTON = "[data-qa='vc-footer-Done']"

# Client-portal link page (public live site, direct - no cp_iframe)
CONTINUE_BUTTON = ".continue-btn"
ACTIVE_DIALOG = ".v-dialog__content.v-dialog__content--active"
MOCK_SUBMIT = "button[type=submit]"
SUCCESS_PAGE = ".done-loading[data-qa='payment-success-page']"
SUCCESS_TITLE = "span.briliant"

# Back-office payment page (Angular billing iframe)
PAY_NAME = "div.summary-header h3"
PAY_AMOUNT = "div.summary-header h2 span"
PAY_TYPE = "div.entity-summary-row .icon-v + div span.caption.wrap"
PAY_ITEM = "span.invoice-item-content-title"


def _scope_with(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    """Return the scope (page or frame) that currently contains `selector`."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            try:
                if scope.locator(selector).count() > 0:
                    return scope
            except Exception:
                continue
        time.sleep(0.1)
    return None


# --------------------------------------------------------------------------- #
# Back office — POS grab QR link
# --------------------------------------------------------------------------- #
def _add_service_to_sale(page: Page, service_name: str) -> None:
    """Reveal the service in the POS Services catalog and add it to the sale."""
    scope = _scope_with(page, CATALOG_ITEM(service_name), timeout=LOAD_TIMEOUT)
    if scope is None:
        raise AssertionError(f"POS catalog item '{service_name}' did not appear")
    card = scope.locator(CATALOG_ITEM(service_name)).first
    card.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    # The add-item button is revealed on hover (legacy hoverElement + add).
    card.hover(timeout=FAST_UI_TIMEOUT)
    add = card.locator(ADD_ITEM).first
    try:
        add.click(timeout=FAST_UI_TIMEOUT)
    except Exception:
        add.evaluate("(el) => el.click()")


def _app_base(context: dict) -> str:
    return (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")


def grab_qr_link(page: Page, context: dict, *, service_name: str, client_name: str) -> str:
    """Open the POS for the client, add the paid service, and grab the QR payment link.

    Mirrors legacy QuickActions.takeSalePayment + Pos.selectItems + Pos.grabQrCodeLink.
    Returns the absolute client-portal payment link read from the QR dialog.
    """
    # Start from a clean top-level page: the preceding mock-gateway save leaves the
    # providers dialog briefly open, which would intercept the Quick Actions click.
    page.goto(f"{_app_base(context)}/app/dashboard", wait_until="domcontentloaded")

    button = _require(page, QUICK_ACTIONS_BUTTON, "Quick Actions button", timeout=LOAD_TIMEOUT)
    button.click(timeout=FAST_UI_TIMEOUT)
    take_payment = _require(page, TAKE_PAYMENT_ITEM, "Take payment (POS) quick action")
    take_payment.click(timeout=FAST_UI_TIMEOUT)

    _select_client(page, client_name)

    # The Services tab is the default active catalog tab (index 0).
    _require(page, SERVICES_TAB_PANEL, "POS Services catalog tab", timeout=LOAD_TIMEOUT)
    _add_service_to_sale(page, service_name)

    activator = _require(page, CHECKOUT_ACTIVATOR, "POS checkout activator", timeout=LOAD_TIMEOUT)
    activator.click(timeout=FAST_UI_TIMEOUT)
    _require(page, CHECKOUT_ACTION_QR, "Pay with QR code action").click(timeout=FAST_UI_TIMEOUT)

    return _read_qr_link(page)


def _read_qr_link(page: Page) -> str:
    """Read the absolute payment URL from the QR dialog's `data-link` element.

    The QR dialog renders the link onto the element that generates the QR code; poll
    for any element exposing a non-empty `data-link` (the QR is populated async)."""
    deadline = time.monotonic() + LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            for selector in (QR_LINK_CONTAINER, QR_LINK_ANY):
                try:
                    locator = scope.locator(selector)
                    for index in range(locator.count()):
                        link = locator.nth(index).get_attribute("data-link")
                        if link:
                            return link
                except Exception:
                    continue
        time.sleep(0.2)
    raise AssertionError("QR dialog did not expose a data-link payment URL")


# --------------------------------------------------------------------------- #
# Client portal — pay the grabbed link in a separate tab
# --------------------------------------------------------------------------- #
def pay_via_link(page: Page, link: str) -> None:
    """Pay the grabbed QR link through the client-portal page in a fresh tab.

    Mirrors legacy: open the link in a new window, raise the active dialog z-index so
    the continue button is clickable, proceed (opens the mock-gateway popup), submit
    the popup, and confirm the mobile payment success page. Uses a fresh browser
    context as the "another tab"; the success selectors are shared across viewports.
    """
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    cp_page = cp_context.new_page()
    try:
        cp_page.goto(link, wait_until="domcontentloaded")

        proceed = cp_page.locator(CONTINUE_BUTTON).first
        proceed.wait_for(state="visible", timeout=NAV_TIMEOUT)

        # Raise the active overlay z-index so it cannot intercept the continue click.
        active = cp_page.locator(ACTIVE_DIALOG).first
        if active.count() > 0:
            try:
                active.evaluate("(el) => { el.style.zIndex = '2000'; }")
            except Exception:
                pass

        with cp_page.context.expect_page(timeout=PAYMENT_PROPAGATE_TIMEOUT) as popup_info:
            proceed.click(timeout=FAST_UI_TIMEOUT)
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded")
        submit = popup.locator(MOCK_SUBMIT).first
        submit.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
        submit.click()
        try:
            popup.wait_for_event("close", timeout=PAYMENT_PROPAGATE_TIMEOUT)
        except Exception:
            pass

        cp_page.locator(SUCCESS_PAGE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
        expect(cp_page.locator(SUCCESS_TITLE).first).to_be_visible(timeout=FAST_UI_TIMEOUT)
    finally:
        cp_context.close()


# --------------------------------------------------------------------------- #
# Back office — QR dialog success
# --------------------------------------------------------------------------- #
def assert_qr_dialog_success(page: Page) -> None:
    """Verify the back-office QR dialog shows payment success, then click Done.

    The dialog updates once the link payment propagates to the back office, so the
    received signal is polled with the eventual-consistency budget."""
    received = _require(
        page, QR_PAYMENT_RECEIVED, "QR dialog payment-received", timeout=PAYMENT_PROPAGATE_TIMEOUT
    )
    received.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    _require(page, QR_DONE_BUTTON, "QR dialog Done button").click(timeout=FAST_UI_TIMEOUT)


# --------------------------------------------------------------------------- #
# Back office — payment page
# --------------------------------------------------------------------------- #
def assert_payment_page(
    page: Page,
    *,
    search_term: str,
    name: str,
    amount: str,
    payment_type: str,
    items: list[str],
) -> None:
    """Open the payment from Payments Received and verify name, amount, type, items."""
    scope = open_payment_by_name(page, search_term, name)

    expect(scope.locator(PAY_NAME).first).to_have_text(name, timeout=FAST_UI_TIMEOUT)
    expect(scope.locator(PAY_AMOUNT).first).to_have_text(amount, timeout=FAST_UI_TIMEOUT)
    expect(scope.locator(PAY_TYPE).first).to_have_text(payment_type, timeout=FAST_UI_TIMEOUT)

    item_locator = scope.locator(PAY_ITEM)
    item_locator.first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    actual_items = sorted((text or "").strip() for text in item_locator.all_inner_texts())
    expected_items = sorted(items)
    if actual_items != expected_items:
        raise AssertionError(
            f"payment items: expected {expected_items}, got {actual_items}"
        )
