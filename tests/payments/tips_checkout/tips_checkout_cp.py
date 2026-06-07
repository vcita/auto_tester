"""Client-portal tipping UI flows for the tips_checkout migration (VCITA2-13899).

Covers tips.feature scenario 3 ("take payment with tips in cp via pay link"):
- a new client pays a service through the public CP make-payment form, adding a
  percent tip in the Vue checkout dialog and paying via the mock-gateway popup, and
- an existing client closes their outstanding balance from the CP payments list,
  adding a custom tip and paying via the mock-gateway popup.

Reuses the CP session/navigation/mock-popup pattern from ``coupons_checkout_cp`` (Vue
CP inside ``#cp_iframe`` + external ``light-payment-gateway`` popup). The checkout tip
bar has no product data-qa, so the stable legacy CSS from clientPortalDialogs is reused
(percent segment buttons / custom-tip modal) and documented.
"""

from __future__ import annotations

from playwright.sync_api import Page

from tests.payments.coupons_checkout.coupons_checkout_cp import (
    CHECKOUT_BTN,
    CHECKOUT_DIALOG,
    CP_IFRAME,
    NAV_TIMEOUT,
    PAYMENTS_MENU,
    PERFORM_PAYMENT,
    POPUP_TIMEOUT,
    SUCCESS_AMOUNT,
    SUCCESS_PAGE,
    SUCCESS_TITLE,
    UI_TIMEOUT,
    open_portal,
)
from tests.sales.estimates.estimates_helpers import CP_VITRAGE, pivot_uid

UNPAID_TAB = '[data-qa="tab-selector-pending"]'

# CP bookings / meeting follow-up tip (scenario 4)
BOOKINGS_MENU = "[data-qa='client-area-menu-bookings']"
PAST_TAB = '[data-qa="tab-selector-past"]'
BOOKING_TITLE = '.booking-title:has-text("{name}")'
ADD_TIP_BTN = '[data-qa="addTip"]'
# Follow-up tip uses the legacy Tips.vue component (NOT the new checkout-tips segments).
FOLLOWUP_TIP_PERCENT = 'xpath=//div[@class="tip-first-line" and contains(.,"{label}")]'
TIP_SUCCESS_TITLE = "Thank you for tipping!"

# Public CP make-payment form (client identity fields by label; pay button by data-qa/class/text).
PAY_FORM_EMAIL = 'xpath=//label[contains(.,"Email")]/../input'
PAY_FORM_FIRST_NAME = 'xpath=//label[contains(.,"First Name")]/../input'
PAY_FORM_PAY_BTN = "[data-qa='payButton'], .checkout-btn"

# Checkout tip bar (Vue CP; no data-qa, stable legacy CSS from clientPortalDialogs).
TIP_SEGMENT = "button.checkout-tips__segment"
TIP_PERCENT_SEGMENT = 'button.checkout-tips__segment:has-text("{label}")'
TIP_CUSTOM_SEGMENT = ".checkout-tips__bar .checkout-tips__segment:last-child"
TIP_CUSTOM_MODAL_INPUT = ".v-text-field__slot input"
TIP_CUSTOM_APPLY = "button.action-dialog__apply-btn"


def open_payment_form(page: Page, context: dict, *, pay_for: str, amount: str):
    """Open a fresh CP browser context on the public make-payment form. Returns (cp_page, cp_context)."""
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    cp_page = cp_context.new_page()
    url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/make-payment?title={pay_for}&amount={amount}"
    cp_page.goto(url, wait_until="domcontentloaded")
    return cp_page, cp_context


def _select_tip_and_pay(cp_page: Page, *, tip_option: str | None = None,
                        tip_amount: str | None = None) -> None:
    """In the open CP checkout dialog: pick a percent tip or enter a custom tip, then
    proceed to payment and submit the mock-gateway popup."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    cp_frame.locator(CHECKOUT_DIALOG).first.wait_for(state="visible", timeout=NAV_TIMEOUT)

    if tip_option:
        segment = cp_frame.locator(TIP_PERCENT_SEGMENT.format(label=tip_option)).first
        segment.wait_for(state="visible", timeout=UI_TIMEOUT)
        segment.click()
    if tip_amount:
        custom = cp_frame.locator(TIP_CUSTOM_SEGMENT).first
        custom.wait_for(state="visible", timeout=UI_TIMEOUT)
        custom.click()
        modal_input = cp_frame.locator(TIP_CUSTOM_MODAL_INPUT).first
        modal_input.wait_for(state="visible", timeout=UI_TIMEOUT)
        modal_input.fill(str(tip_amount))
        cp_frame.locator(TIP_CUSTOM_APPLY).first.click()

    proceed = cp_frame.locator(PERFORM_PAYMENT).first
    proceed.wait_for(state="visible", timeout=UI_TIMEOUT)
    with cp_page.context.expect_page(timeout=POPUP_TIMEOUT) as popup_info:
        proceed.click()
    popup = popup_info.value
    popup.wait_for_load_state("domcontentloaded")
    submit = popup.locator("button[type=submit]").first
    submit.wait_for(state="visible", timeout=UI_TIMEOUT)
    submit.click()
    try:
        popup.wait_for_event("close", timeout=POPUP_TIMEOUT)
    except Exception:
        pass


def pay_via_payment_form(page: Page, context: dict, *, pay_for: str, amount: str,
                         first_name: str, email: str, tip_option: str) -> None:
    """New client pays a service via the public CP make-payment form with a percent tip."""
    cp_page, cp_context = open_payment_form(page, context, pay_for=pay_for, amount=amount)
    try:
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        email_input = cp_frame.locator(PAY_FORM_EMAIL).first
        email_input.wait_for(state="visible", timeout=NAV_TIMEOUT)
        email_input.fill(email)
        cp_frame.locator(PAY_FORM_FIRST_NAME).first.fill(first_name)
        cp_frame.locator(PAY_FORM_PAY_BTN).first.click()
        _select_tip_and_pay(cp_page, tip_option=tip_option)
    finally:
        cp_context.close()


def close_balance_via_cp(page: Page, context: dict, *, portal_token: str,
                         tip_amount: str) -> None:
    """Existing client closes their CP balance from the payments list with a custom tip."""
    cp_page, cp_context = open_portal(page, context, portal_token)
    try:
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        payments = cp_frame.locator(PAYMENTS_MENU).first
        payments.wait_for(state="visible", timeout=NAV_TIMEOUT)
        payments.click()
        unpaid = cp_frame.locator(UNPAID_TAB).first
        unpaid.wait_for(state="visible", timeout=NAV_TIMEOUT)
        unpaid.click()
        checkout = cp_frame.locator(CHECKOUT_BTN).first
        checkout.wait_for(state="visible", timeout=NAV_TIMEOUT)
        checkout.click()
        _select_tip_and_pay(cp_page, tip_amount=tip_amount)
    finally:
        cp_context.close()


def add_meeting_followup_tip(page: Page, context: dict, *, portal_token: str,
                            meeting_name: str, tip_option: str,
                            expected_amount: str) -> None:
    """Existing client adds a follow-up tip to a paid past meeting from the CP and
    verifies the tip payment-success page.

    Bookings -> Past tab -> open the meeting -> Add a tip -> pick the percent tip in the
    legacy Tips.vue bar -> pay via the mock-gateway popup -> assert the success page shows
    the tip title and ``Amount received: <expected_amount>``."""
    cp_page, cp_context = open_portal(page, context, portal_token)
    try:
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        bookings = cp_frame.locator(BOOKINGS_MENU).first
        bookings.wait_for(state="visible", timeout=NAV_TIMEOUT)
        bookings.click()
        past = cp_frame.locator(PAST_TAB).first
        past.wait_for(state="visible", timeout=NAV_TIMEOUT)
        past.click()
        meeting = cp_frame.locator(BOOKING_TITLE.format(name=meeting_name)).first
        meeting.wait_for(state="visible", timeout=NAV_TIMEOUT)
        meeting.click()
        add_tip = cp_frame.locator(ADD_TIP_BTN).first
        add_tip.wait_for(state="visible", timeout=NAV_TIMEOUT)
        add_tip.click()

        cp_frame.locator(CHECKOUT_DIALOG).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
        tip = cp_frame.locator(FOLLOWUP_TIP_PERCENT.format(label=tip_option)).first
        tip.wait_for(state="visible", timeout=UI_TIMEOUT)
        tip.click()
        proceed = cp_frame.locator(PERFORM_PAYMENT).first
        proceed.wait_for(state="visible", timeout=UI_TIMEOUT)
        with cp_page.context.expect_page(timeout=POPUP_TIMEOUT) as popup_info:
            proceed.click()
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded")
        submit = popup.locator("button[type=submit]").first
        submit.wait_for(state="visible", timeout=UI_TIMEOUT)
        submit.click()
        try:
            popup.wait_for_event("close", timeout=POPUP_TIMEOUT)
        except Exception:
            pass

        _assert_tip_success(cp_frame, expected_amount=expected_amount)
    finally:
        cp_context.close()


def _assert_tip_success(cp_frame, *, expected_amount: str) -> None:
    cp_frame.locator(SUCCESS_PAGE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    title = cp_frame.locator(SUCCESS_TITLE).first.inner_text().strip()
    if title != TIP_SUCCESS_TITLE:
        raise AssertionError(f"CP tip success title mismatch: expected {TIP_SUCCESS_TITLE!r}, got {title!r}")
    amount = cp_frame.locator(SUCCESS_AMOUNT).first.inner_text().strip()
    expected_text = f"Amount received: {expected_amount}"
    if amount != expected_text:
        raise AssertionError(f"CP tip success amount mismatch: expected {expected_text!r}, got {amount!r}")
