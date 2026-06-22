"""Client-portal checkout helpers for the coupons_checkout subcategory.

Drives the two legacy CP coupon-payment flows (Vue client portal, inside `#cp_iframe`):
- pay a single past meeting via its "Pay" action (legacy "client selects an action in
  meeting page" + "client pays for meeting"), and
- close the whole outstanding balance from the payments list (legacy "client closes
  payment balance in cp"),
both applying a coupon in the CPPaymentDialog and paying through the mock-gateway popup,
then asserting the CP payment-success page.

Also creates a service-scoped coupon through the Angular Settings/Coupons UI (legacy
"user creates new coupon") for the one scenario that exercises coupon creation in the UI.

Selector policy: data-qa first (menus, tabs, perform-payment). The Vue CPPaymentDialog
coupon section and the Angular coupon settings expose no data-qa, so stable legacy CSS is
reused and documented; data-qa should be added in product code (see changelog/script).
Element/interaction waits are capped at 5s; navigation and the external mock-gateway popup
use a longer, justified readiness budget.
"""

from __future__ import annotations

from playwright.sync_api import Page

from tests.salsa.payments.coupons.coupons_helpers import (
    COUPON_AMOUNT_INPUT,
    COUPON_NAME_INPUT,
    COUPON_TYPE_SELECT,
    CREATE_COUPON_BUTTON,
    SAVE_COUPON_BUTTON,
    _pick_option,
    open_coupons_settings,
)
from tests.salsa.sales.estimates.estimates_helpers import CP_VITRAGE, pivot_uid

UI_TIMEOUT = 5000
NAV_TIMEOUT = 20000  # CP (re)navigation / list render readiness — not an element-interaction wait
POPUP_TIMEOUT = 20000  # external mock-gateway popup round trip

CP_IFRAME = "#cp_iframe"

# CP navigation (data-qa). The CP side menu is the expanded sidebar at the
# 1440-wide context the runner uses (verified live), so the menu items are visible.
BOOKINGS_MENU = "[data-qa='client-area-menu-bookings']"
PAYMENTS_MENU = "[data-qa='client-area-menu-payments']"
PAST_TAB = '[data-qa="tab-selector-past"]'
UNPAID_TAB = '[data-qa="tab-selector-pending"]'
PERFORM_PAYMENT = '[data-qa="perform-payment-action"]'

# CP bookings list (new Vue CP): each past booking card carries title="<service>" and
# exposes its own "Pay" action (data-qa="pay") inline -- there is no separate meeting page.
BOOKING_LIST_ITEM = ".booking-list-item.list-item"
BOOKING_PAY_ACTION = '[data-qa="pay"]'

# CP payments list -- close the whole outstanding balance.
CHECKOUT_BTN = ".checkout-btn"

# CPPaymentDialog coupon section (Vue CP; no data-qa, stable component CSS).
CHECKOUT_DIALOG = ".checkout-dialog"
COUPON_SECTION_CLICKABLE = ".coupon-section__clickable"
COUPON_CODE_INPUT = ".coupon-input input"
COUPON_APPLY_BTN = "button.action-dialog__apply-btn"
COUPON_APPLIED_TITLE = ".coupon-section__applied-title"
MOCK_SUBMIT = "button[type=submit]"

# CP payment-success page
SUCCESS_PAGE = "[data-qa='payment-success-page']"
SUCCESS_TITLE = "span.briliant"
SUCCESS_SUBTITLE = "span.thanks"
SUCCESS_AMOUNT = "span.paymet-text"

# Angular Settings/Coupons UI — service-scoped coupon creation.
# Checking "Limit coupon to specific services" reveals a multi-select of services; the
# coupon code is auto-generated into the dialog's Code field (read it there directly).
CODE_INPUT = 'input[name="code"]'
LIMIT_SERVICES_CHECKBOX = 'md-checkbox[ng-model="newCoupon.has_selected_services"]'
SERVICE_SELECT = "md-select.ellipsis"
PROMOTE_DISMISS = (
    'md-dialog-actions button[translate="settings.coupons.coupon_ready.close"], '
    'md-dialog-actions button[ng-click="cancel()"]'
)


# --------------------------------------------------------------------------- #
# Client portal session
# --------------------------------------------------------------------------- #
def open_portal(page: Page, context: dict, portal_token: str):
    """Open a fresh client-portal browser context for the client. Returns (cp_page, cp_context)."""
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    cp_page = cp_context.new_page()
    url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/action?client_jwt={portal_token}"
    cp_page.goto(url, wait_until="domcontentloaded")
    return cp_page, cp_context


# --------------------------------------------------------------------------- #
# Coupon apply + pay (shared by both CP flows)
# --------------------------------------------------------------------------- #
def _apply_coupon_and_pay(cp_page: Page, coupon_code: str) -> None:
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    cp_frame.locator(CHECKOUT_DIALOG).first.wait_for(state="visible", timeout=NAV_TIMEOUT)

    coupon_open = cp_frame.locator(COUPON_SECTION_CLICKABLE).first
    coupon_open.wait_for(state="visible", timeout=UI_TIMEOUT)
    coupon_open.click()

    code_input = cp_frame.locator(COUPON_CODE_INPUT).last
    code_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    code_input.fill(coupon_code)

    apply_btn = cp_frame.locator(COUPON_APPLY_BTN).first
    apply_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    apply_btn.click()

    # Coupon applied confirmation is the client-side signal the discount took effect.
    cp_frame.locator(COUPON_APPLIED_TITLE).first.wait_for(state="visible", timeout=UI_TIMEOUT)

    proceed = cp_frame.locator(PERFORM_PAYMENT).first
    proceed.wait_for(state="visible", timeout=UI_TIMEOUT)
    with cp_page.context.expect_page(timeout=POPUP_TIMEOUT) as popup_info:
        proceed.click()
    popup = popup_info.value
    popup.wait_for_load_state("domcontentloaded")
    submit = popup.locator(MOCK_SUBMIT).first
    submit.wait_for(state="visible", timeout=UI_TIMEOUT)
    submit.click()
    try:
        popup.wait_for_event("close", timeout=POPUP_TIMEOUT)
    except Exception:
        pass


def pay_meeting_with_coupon(cp_page: Page, meeting_name: str, coupon_code: str) -> None:
    """Open the Past bookings tab, click the meeting's inline "Pay", apply the coupon and pay.

    New Vue CP: the bookings menu lands on the (empty) Upcoming tab, so switch to Past first,
    then act on the booking card identified by its title="<service>" and its inline Pay action.
    """
    cp_frame = cp_page.frame_locator(CP_IFRAME)

    bookings = cp_frame.locator(BOOKINGS_MENU).first
    bookings.wait_for(state="visible", timeout=NAV_TIMEOUT)
    bookings.click()

    past_tab = cp_frame.locator(PAST_TAB).first
    past_tab.wait_for(state="visible", timeout=NAV_TIMEOUT)
    past_tab.click()

    card = cp_frame.locator(f'{BOOKING_LIST_ITEM}[title="{meeting_name}"]').first
    card.wait_for(state="visible", timeout=NAV_TIMEOUT)
    pay_action = card.locator(BOOKING_PAY_ACTION).first
    pay_action.wait_for(state="visible", timeout=UI_TIMEOUT)
    pay_action.click()

    _apply_coupon_and_pay(cp_page, coupon_code)


def close_balance_with_coupon(cp_page: Page, coupon_code: str) -> None:
    """Open the payments list Unpaid tab (items pre-selected), checkout, apply coupon and pay."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)

    payments = cp_frame.locator(PAYMENTS_MENU).first
    payments.wait_for(state="visible", timeout=NAV_TIMEOUT)
    payments.click()

    unpaid_tab = cp_frame.locator(UNPAID_TAB).first
    unpaid_tab.wait_for(state="visible", timeout=NAV_TIMEOUT)
    unpaid_tab.click()

    checkout = cp_frame.locator(CHECKOUT_BTN).first
    checkout.wait_for(state="visible", timeout=NAV_TIMEOUT)
    checkout.click()

    _apply_coupon_and_pay(cp_page, coupon_code)


def assert_payment_success(cp_page: Page, *, title: str, subtitle: str, amount: str) -> None:
    """Verify the CP payment-success page title, subtitle, and 'Amount received: $X.XX'."""
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    cp_frame.locator(SUCCESS_PAGE).first.wait_for(state="visible", timeout=NAV_TIMEOUT)

    title_el = cp_frame.locator(SUCCESS_TITLE).first
    title_el.wait_for(state="visible", timeout=UI_TIMEOUT)
    actual_title = (title_el.inner_text(timeout=UI_TIMEOUT) or "").strip()
    if title not in actual_title:
        raise AssertionError(f"Success title: expected '{title}', got '{actual_title}'")

    subtitle_el = cp_frame.locator(SUCCESS_SUBTITLE).first
    subtitle_el.wait_for(state="visible", timeout=UI_TIMEOUT)
    actual_subtitle = (subtitle_el.inner_text(timeout=UI_TIMEOUT) or "").strip()
    if subtitle not in actual_subtitle:
        raise AssertionError(f"Success subtitle: expected '{subtitle}', got '{actual_subtitle}'")

    amount_el = cp_frame.locator(SUCCESS_AMOUNT).first
    amount_el.wait_for(state="visible", timeout=UI_TIMEOUT)
    actual_amount = (amount_el.inner_text(timeout=UI_TIMEOUT) or "").strip()
    if amount not in actual_amount:
        raise AssertionError(f"Success amount: expected to contain '{amount}', got '{actual_amount}'")


# --------------------------------------------------------------------------- #
# Service-scoped coupon creation via the Angular Settings/Coupons UI (legacy S3)
# --------------------------------------------------------------------------- #
def create_service_coupon_ui(
    page: Page, coupon_type: str, name: str, amount: str, service_name: str
) -> str:
    """Create a service-scoped coupon through Settings/Coupons and return its generated code.

    New coupon dialog: pick type, fill name/amount, read the auto-generated code, then check
    "Limit coupon to specific services" and pick the service from the (multi-select) dropdown.
    The multi-select stays open after picking, so dismiss it (Escape) before Save, otherwise its
    overlay intercepts the Save click.
    """
    scope = open_coupons_settings(page)
    scope.locator(CREATE_COUPON_BUTTON).first.click()
    _pick_option(scope, COUPON_TYPE_SELECT, coupon_type)
    scope.locator(COUPON_NAME_INPUT).first.fill(name)
    scope.locator(COUPON_AMOUNT_INPUT).first.fill(amount)

    code_el = scope.locator(CODE_INPUT).first
    code_el.wait_for(state="visible", timeout=UI_TIMEOUT)
    code = (code_el.input_value(timeout=UI_TIMEOUT) or "").strip()
    if not code:
        raise AssertionError("Could not read the auto-generated coupon code from the create dialog")

    scope.locator(LIMIT_SERVICES_CHECKBOX).first.locator(".md-container").click()
    _pick_option(scope, SERVICE_SELECT, service_name)
    page.keyboard.press("Escape")
    save_btn = scope.locator(SAVE_COUPON_BUTTON).first
    save_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    save_btn.click()

    dismiss = scope.locator(PROMOTE_DISMISS).first
    dismiss.wait_for(state="visible", timeout=NAV_TIMEOUT)
    dismiss.click()
    return code
