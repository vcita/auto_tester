"""Setup-only UI flow for offset_fees: save a card on file.

Saving a card is an account prerequisite (not the feature under test): the CP
checkout fee badge is shown on the selected saved card. It mirrors the legacy
`addCreditCard` flow. ACH/credit-card enablement is provisioned via the
payment-settings API (see offset_fees_api.enable_card_and_ach).
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

from tests.salsa.payments.offset_fees.offset_fees_ui import (
    FAST_UI_TIMEOUT,
    click_via_dom,
    find_control,
    first_visible,
    frame_with,
)

# The client page renders three nested iframes (POV > Angular > Vue), so its tabs
# can take noticeably longer than a single in-page interaction; this is a page-load
# readiness budget (akin to login waiting for the dashboard), not an element wait.
CLIENT_PAGE_LOAD_TIMEOUT = 15000
PAYMENTS_TAB = 'div.v-tab:has-text("Payments")'
ADD_CARD_EMPTY_STATE = "div.empty-state-cta.empty-state-content"
ADD_CARD_DIALOG = '[data-qa="add-payment-method-dialog"]'
GATEWAY_CARD_INPUT = "#card"
CARD_CONSENT = ".v-input--selection-controls__input"
ADD_CARD_BUTTON = 'button[data-qa="vc-footer-Add card"]'
MOCK_CARD_NUMBER = "4111111111111111"


def save_card_on_file(page: Page, context: dict, client_id: str) -> None:
    """Save a mock-gateway credit card on the client's card so a saved card exists.

    The client page tabs and the card-on-file empty state live in the inner Vue
    iframe; the Payments tab must be selected before the add-card CTA renders.
    """
    base = (context.get("base_url") or "").rstrip("/")
    page.goto(f"{base}/app/clients/{client_id}", wait_until="domcontentloaded")

    payments_tab = find_control(page, PAYMENTS_TAB, timeout=CLIENT_PAGE_LOAD_TIMEOUT)
    if payments_tab is None:
        raise AssertionError("Payments tab did not appear on the client page")
    payments_tab.click(timeout=FAST_UI_TIMEOUT)

    open_cta = find_control(page, ADD_CARD_EMPTY_STATE, timeout=FAST_UI_TIMEOUT)
    if open_cta is None:
        raise AssertionError("Add-card empty-state CTA did not appear on the client page")
    open_cta.click(timeout=FAST_UI_TIMEOUT)

    if find_control(page, ADD_CARD_DIALOG, timeout=FAST_UI_TIMEOUT) is None:
        raise AssertionError("Add payment method dialog did not open")

    gateway_scope = frame_with(page, GATEWAY_CARD_INPUT, timeout=FAST_UI_TIMEOUT)
    if gateway_scope is None:
        raise AssertionError("Mock gateway card-number iframe did not load")
    card_input = gateway_scope.locator(GATEWAY_CARD_INPUT).first
    card_input.fill(MOCK_CARD_NUMBER, timeout=FAST_UI_TIMEOUT)

    consent = find_control(page, f"{ADD_CARD_DIALOG} {CARD_CONSENT}", timeout=FAST_UI_TIMEOUT)
    if consent is None:
        consent = find_control(page, CARD_CONSENT, timeout=FAST_UI_TIMEOUT)
    if consent is not None:
        click_via_dom(consent)

    add_button = find_control(page, ADD_CARD_BUTTON, timeout=FAST_UI_TIMEOUT)
    if add_button is None:
        raise AssertionError("Add card button did not appear")
    add_button.click(timeout=FAST_UI_TIMEOUT)
    _wait_card_saved(page)


def _wait_card_saved(page: Page) -> None:
    """Wait for the add-card dialog to close, the readiness signal for a saved card."""
    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if first_visible([scope.locator(ADD_CARD_DIALOG) for scope in [page, *page.frames]], timeout=200) is None:
            return
        time.sleep(0.2)
