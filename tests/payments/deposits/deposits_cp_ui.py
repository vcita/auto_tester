"""Client-portal UI flows for the estimate-deposit scenarios (deposits #4 sign+pay, #5 offline).

Opens the client portal as the client (JWT in URL), reads the estimate deposit state
(DUE / PAID / OFFLINE), and drives the client actions: sign + pay the deposit through the
mock gateway popup, or approve an offline (can't-pay-online) deposit. The portal renders
inside the `#cp_iframe`; the mock gateway opens an external popup window. Explicit UI waits
are capped at 5s; portal (re)navigation uses a longer page-readiness budget.
"""

from __future__ import annotations

from playwright.sync_api import Page

from tests.sales.estimates.estimates_helpers import CP_VITRAGE, NAV_TIMEOUT, pivot_uid

FAST_UI_TIMEOUT = 5000
POPUP_TIMEOUT = 20000

CP_IFRAME = "#cp_iframe"
ESTIMATES_MENU = '[data-qa="client-area-menu-estimates"]'
ESTIMATES_LIST_PAGE = ".estimates-list-page"
ESTIMATE_TITLE_LINK = "span.payment-title"
TAB_DONE = 'div[tab="done"]'
ENTITY_PAGE = ".payment-entity-page"

# Deposit display (CP estimate entity page)
DEPOSIT_DESC = 'span[data-qa="deposit-description"]'
DEPOSIT_DESC_PAID = 'span[data-qa="deposit-description-paid"]'
DEPOSIT_AMOUNT = 'span[data-qa="deposit-amount"]'
OFFLINE_NOTICE = ".deposit-warning"

# Client actions
APPROVE_AND_PAY = 'button[data-qa="approve-and-pay"]'
APPROVE = 'button[data-qa="approve"]'
DIALOG_APPROVE_CONFIRM = "button.approve-button-text"
SIGNATURE_CANVAS = 'div[data-qa="signature-container"] canvas'
APPROVE_SIGNATURE = 'button[data-qa="approve-signature"]'
PROCEED_TO_PAYMENT = '[data-qa="perform-payment-action"]'
MOCK_SUBMIT = "button[type=submit]"

# Result pages
SUCCESS_PAGE = "[data-qa='payment-success-page']"
SUCCESS_AMOUNT = "span.paymet-text"
OFFLINE_AMOUNT = ".offline-deposit-container .deposit-amount"


def open_portal(page: Page, context: dict, portal_token: str):
    """Open a fresh client-portal browser context for the client. Returns (cp_page, cp_context)."""
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    cp_page = cp_context.new_page()
    goto_estimates_list(cp_page, context, portal_token)
    return cp_page, cp_context


def goto_estimates_list(cp_page: Page, context: dict, portal_token: str, *, done_tab: bool = False) -> None:
    """(Re)navigate the portal to the estimates list, optionally on the 'done' (approved) tab."""
    url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/action?client_jwt={portal_token}"
    cp_page.goto(url, wait_until="domcontentloaded")
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    menu = cp_frame.locator(ESTIMATES_MENU).first
    menu.wait_for(state="visible", timeout=NAV_TIMEOUT)
    menu.click()
    cp_frame.locator(ESTIMATES_LIST_PAGE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    if done_tab:
        cp_frame.locator(TAB_DONE).first.click(timeout=FAST_UI_TIMEOUT)


def open_estimate(cp_page: Page, title: str):
    """Open the estimate by title from the list and wait for its entity page. Returns the cp frame."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    link = cp_frame.locator(ESTIMATE_TITLE_LINK).filter(has_text=title).first
    link.wait_for(state="visible", timeout=NAV_TIMEOUT)
    link.click()
    cp_frame.locator(ENTITY_PAGE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    return cp_frame


def assert_cp_deposit(cp_page: Page, *, deposit_state: str, deposit_amount: str, can_client_pay: bool = True) -> None:
    """Verify the CP estimate deposit state (DUE/PAID/OFFLINE), amount, and the matching action."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    state = deposit_state.upper()
    if state == "DUE":
        action = APPROVE_AND_PAY if can_client_pay else APPROVE
        cp_frame.locator(action).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    elif state == "OFFLINE":
        cp_frame.locator(OFFLINE_NOTICE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)

    desc = cp_frame.locator(DEPOSIT_DESC_PAID if state == "PAID" else DEPOSIT_DESC).first
    desc.wait_for(state="visible", timeout=NAV_TIMEOUT)
    amount_el = cp_frame.locator(DEPOSIT_AMOUNT).first
    amount_el.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    actual = (amount_el.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    if deposit_amount not in actual:
        raise AssertionError(f"CP deposit amount: expected '{deposit_amount}', got '{actual}'")


def _sign(cp_page: Page) -> None:
    """Draw a signature stroke on the canvas and approve it."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    canvas = cp_frame.locator(SIGNATURE_CANVAS).first
    canvas.wait_for(state="visible", timeout=NAV_TIMEOUT)
    box = canvas.bounding_box()
    if not box:
        raise AssertionError("Signature canvas has no bounding box")
    start_x, start_y = box["x"] + 15, box["y"] + 15
    cp_page.mouse.move(start_x, start_y)
    cp_page.mouse.down()
    cp_page.mouse.move(start_x + 80, start_y + 40, steps=10)
    cp_page.mouse.move(start_x + 140, start_y + 10, steps=10)
    cp_page.mouse.up()
    cp_frame.locator(APPROVE_SIGNATURE).first.click(timeout=FAST_UI_TIMEOUT)


def sign_and_pay_deposit(cp_page: Page) -> None:
    """Approve+pay the deposit: sign, then pay through the mock gateway popup."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    cp_frame.locator(APPROVE_AND_PAY).first.click(timeout=FAST_UI_TIMEOUT)
    _sign(cp_page)
    # Proceeding to payment opens the external mock-gateway popup; submit it and wait for it to close.
    proceed = cp_frame.locator(PROCEED_TO_PAYMENT).first
    proceed.wait_for(state="visible", timeout=NAV_TIMEOUT)
    with cp_page.context.expect_page(timeout=POPUP_TIMEOUT) as popup_info:
        proceed.click(timeout=FAST_UI_TIMEOUT)
    popup = popup_info.value
    popup.wait_for_load_state("domcontentloaded")
    submit = popup.locator(MOCK_SUBMIT).first
    submit.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    submit.click()
    try:
        popup.wait_for_event("close", timeout=POPUP_TIMEOUT)
    except Exception:
        pass


def assert_payment_success(cp_page: Page, amount: str) -> None:
    """Verify the payment success page shows the expected amount received."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    cp_frame.locator(SUCCESS_PAGE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    text_el = cp_frame.locator(SUCCESS_AMOUNT).first
    text_el.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    actual = (text_el.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    if amount not in actual:
        raise AssertionError(f"Payment success amount: expected '{amount}', got '{actual}'")


def approve_offline(cp_page: Page) -> None:
    """Approve an offline (can't-pay-online) deposit estimate via the confirm dialog."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    cp_frame.locator(APPROVE).first.click(timeout=FAST_UI_TIMEOUT)
    cp_frame.locator(DIALOG_APPROVE_CONFIRM).first.click(timeout=NAV_TIMEOUT)


def assert_offline_deposit_page(cp_page: Page, amount: str) -> None:
    """Verify the client is on the offline-deposit page showing the expected amount."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    amount_el = cp_frame.locator(OFFLINE_AMOUNT).first
    amount_el.wait_for(state="visible", timeout=NAV_TIMEOUT)
    actual = (amount_el.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()
    if amount not in actual:
        raise AssertionError(f"Offline deposit amount: expected '{amount}', got '{actual}'")
