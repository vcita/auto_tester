"""POS Pay-with-QR flow: open the POS, add a service, grab the QR payment link,
pay it from a second tab via the mock gateway, and confirm the QR dialog success.

Mirrors the legacy Pos / QrCodePaymentDialog / ClientPortalLinkCheckout chain.
The POS and its QR dialog live in the frontage document nesting (POV top, Angular
client-picker in an iframe), so controls are resolved across the page and all of
its frames. Normal UI waits are capped at 5s; the realtime QR-dialog payment-received
push is an eventual-consistency websocket signal and gets a longer poll budget
(the legacy waited 90s on it), and the second-tab gateway round trip gets a load budget.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

FAST_UI_TIMEOUT = 5000
TAB_LOAD_TIMEOUT = 20000
# Realtime websocket push from the paid link back to the open POS QR dialog; this is
# eventual consistency, not a normal element wait (legacy waited 90s on it).
PAYMENT_RECEIVED_TIMEOUT = 90000

QUICK_ACTIONS_BUTTON = '.quick-actions button, [data-qa="vcMenu-QuickAction"]'
QUICK_ACTIONS_CONTAINER = '[data-qa="VcQuickActions"]'
TAKE_PAYMENT_ITEM = '[data-qa="VcLargeQuickAction-point_of_sale"]'

CLIENT_SEARCH_INPUT = "div.search-clients input"
CLIENT_RESULT = '.md-dialog-container [role="list"]:not([ng-hide]) .main-client-info'

CATALOG_ITEM = '[data-qa="catalog-item-{name}"]'
ADD_ITEM = '[data-qa="catalog-item-{name}"] [data-qa="add-item"]'
BILLABLE_ITEM = ".billable-item-container__name"
CHECKOUT_ACTIVATOR = '[data-qa="checkout-actions-activator"]'
CHECKOUT_QR = '[data-qa="checkout-action-qr"]'

QR_LINK_CONTAINER = ".payment-content[data-link], [data-link].payment-content"
PAYMENT_RECEIVED = "[data-qa='payment-received']"
QR_DONE_BUTTON = "[data-qa='vc-footer-Done']"

CARD_METHOD = '.payment-methods__section, :text("Credit / Debit card")'
PAY_BUTTON = 'button:has-text("Pay $"), .continue-btn'
MOCK_POPUP_SUBMIT = "button[type=submit]"
PAY_SUCCESS = "[data-qa='payment-success-page'], span.briliant, :text('Brilliant')"


def find_control(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
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


def locate_any(page: Page, selector: str):
    """Return the first existing match for `selector` (no visibility requirement)."""
    for scope in [page, *page.frames]:
        try:
            locator = scope.locator(selector)
            if locator.count() > 0:
                return locator.first
        except Exception:
            continue
    return None


def open_pos_with_client(page: Page, context: dict) -> None:
    """Open the POS via Quick Actions and pick the client by full name."""
    base = (context.get("base_url") or "").rstrip("/")
    page.goto(f"{base}/app/dashboard", wait_until="domcontentloaded")

    quick = find_control(page, QUICK_ACTIONS_BUTTON)
    if quick is None:
        raise AssertionError("Quick Actions button did not appear")
    quick.click(timeout=FAST_UI_TIMEOUT)
    if find_control(page, QUICK_ACTIONS_CONTAINER) is None:
        raise AssertionError("Quick Actions menu did not open")

    take_payment = find_control(page, TAKE_PAYMENT_ITEM)
    if take_payment is None:
        raise AssertionError("Take payment (point of sale) quick action did not appear")
    take_payment.click(timeout=FAST_UI_TIMEOUT)

    _pick_client(page, context["created_client_name"])


def add_service_and_grab_qr_link(page: Page, context: dict, service_name: str) -> str:
    """Add the service to the POS sale and grab the Pay-with-QR `data-link`."""
    add_button = find_control(page, ADD_ITEM.format(name=service_name))
    if add_button is None:
        card = find_control(page, CATALOG_ITEM.format(name=service_name))
        if card is None:
            raise AssertionError(f"Catalog item '{service_name}' did not appear in the POS")
        card.hover(timeout=FAST_UI_TIMEOUT)
        add_button = find_control(page, ADD_ITEM.format(name=service_name))
    if add_button is None:
        raise AssertionError(f"Add button for catalog item '{service_name}' did not appear")
    add_button.click(force=True, timeout=FAST_UI_TIMEOUT)

    if find_control(page, BILLABLE_ITEM) is None:
        raise AssertionError("Service was not added to the POS checkout")

    activator = find_control(page, CHECKOUT_ACTIVATOR)
    if activator is None:
        raise AssertionError("Checkout actions activator did not appear")
    activator.click(timeout=FAST_UI_TIMEOUT)

    qr_action = find_control(page, CHECKOUT_QR)
    if qr_action is None:
        raise AssertionError("Pay with QR code action did not appear")
    qr_action.click(timeout=FAST_UI_TIMEOUT)

    return _grab_link(page)


def pay_link_in_new_tab(page: Page, link: str) -> None:
    """Open the payment link in a second tab and pay via the mock gateway.

    The redesigned v2 link checkout opens with the Pay button visible. Clicking it
    opens the mock 'light-payment-gateway' popup (per the legacy windowOpenedAndClosed
    flow); submit it, then wait for the checkout success page.
    """
    tab = page.context.new_page()
    try:
        tab.goto(link, wait_until="domcontentloaded")

        method = find_control(tab, CARD_METHOD, timeout=2000)
        if method is not None:
            try:
                method.click(timeout=FAST_UI_TIMEOUT)
            except Exception:
                pass

        pay = find_control(tab, PAY_BUTTON, timeout=TAB_LOAD_TIMEOUT)
        if pay is None:
            raise AssertionError("Pay button did not appear on the payment link checkout")

        popup = None
        try:
            with tab.context.expect_page(timeout=FAST_UI_TIMEOUT) as popup_info:
                pay.click(timeout=FAST_UI_TIMEOUT)
            popup = popup_info.value
        except Exception:
            pass

        if popup is not None:
            _submit_mock_popup(popup)
            try:
                popup.wait_for_event("close", timeout=TAB_LOAD_TIMEOUT)
            except Exception:
                pass

        if find_control(tab, PAY_SUCCESS, timeout=TAB_LOAD_TIMEOUT) is None:
            raise AssertionError("Payment success page did not appear after paying the link")
    finally:
        tab.close()


def _submit_mock_popup(popup) -> None:
    """Submit the mock gateway popup (some variants ask for a secret/alias)."""
    popup.wait_for_load_state("domcontentloaded")
    for field, value in (("#secret", "bla"), ("#alias", "blu")):
        try:
            if popup.locator(field).count() > 0:
                popup.locator(field).fill(value)
        except Exception:
            pass
    submit = popup.locator(MOCK_POPUP_SUBMIT).first
    submit.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    submit.click()


def confirm_qr_dialog_success(page: Page) -> None:
    """Wait for the POS QR dialog to show payment success (realtime), then click Done."""
    received = find_control(page, PAYMENT_RECEIVED, timeout=PAYMENT_RECEIVED_TIMEOUT)
    if received is None:
        raise AssertionError(
            "QR code dialog did not show payment success (realtime payment-received push)"
        )
    done = find_control(page, QR_DONE_BUTTON)
    if done is not None:
        done.click(timeout=FAST_UI_TIMEOUT)


def _pick_client(page: Page, full_name: str) -> None:
    search = find_control(page, CLIENT_SEARCH_INPUT, timeout=TAB_LOAD_TIMEOUT)
    if search is None:
        raise AssertionError("Client picker search input did not appear")
    search.fill(full_name, timeout=FAST_UI_TIMEOUT)

    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        result = find_control(page, CLIENT_RESULT, timeout=500)
        if result is not None:
            result.click(timeout=FAST_UI_TIMEOUT)
            return
        time.sleep(0.2)
    raise AssertionError(f"Client '{full_name}' did not appear in the client picker")


def _grab_link(page: Page) -> str:
    deadline = time.monotonic() + TAB_LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        container = locate_any(page, QR_LINK_CONTAINER)
        if container is not None:
            link = container.get_attribute("data-link")
            if link:
                return link
        time.sleep(0.2)
    raise AssertionError("QR code dialog did not expose a payment link (data-link)")
