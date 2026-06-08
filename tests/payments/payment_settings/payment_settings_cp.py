"""Client-portal helpers for the Payment Settings migration (VCITA2-13901).

Opens the client portal as a client (reusing the proven `open_portal` flow) and checks
whether the "Payments" client-area action is available — used to verify the
`allow_view_payments` setting. Also opens the public make-payment form and detects the
"no payment method" error dialog used by the disable-credit-card scenario.
"""

import re
import time

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.payments.coupons_checkout.coupons_checkout_cp import open_portal
from tests.sales.adhoc_sale_refund.adhoc_sale_helpers import open_payment_form

FORM_OPEN_RETRIES = 2  # CP make-payment page load can transiently exceed the nav budget

UI_TIMEOUT = 5000
NAV_TIMEOUT = 20000

CP_IFRAME = "#cp_iframe"
PAYMENTS_MENU = "[data-qa='client-area-menu-payments']"
# CP side menu readiness: any client-area menu item means the portal shell has rendered.
CP_MENU_READY = "[data-qa^='client-area-menu-']"

# Make-payment form fields + actions (shared with adhoc-sale CP checkout).
EMAIL_FIELD = '[data-qa="email-input"]'
CHECKOUT_BUTTON_RE = re.compile(r"checkout|pay", re.I)
PROCEED_TO_PAYMENT = '[data-qa="perform-payment-action"]'
# Legacy "no payment error dialog": a modal (role=document) / no-payment-method error.
ERROR_DIALOG = "[role='document'], .error-dialog, [data-qa='no-payment-error']"
NO_PAYMENT_TEXT = re.compile(r"no payment|not available|cannot|unable|no available", re.I)


def _wait_cp_ready(cp_page: Page) -> None:
    cp_frame = cp_page.frame_locator(CP_IFRAME)
    cp_frame.locator(CP_MENU_READY).first.wait_for(state="visible", timeout=NAV_TIMEOUT)


def payments_action_visible(page: Page, context: dict, portal_token: str) -> bool:
    """Open the portal as the client and report whether the Payments action is present."""
    cp_page, cp_context = open_portal(page, context, portal_token)
    try:
        _wait_cp_ready(cp_page)
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        # Give a brief settle for all menu items to render before counting.
        deadline = time.monotonic() + UI_TIMEOUT / 1000
        present = cp_frame.locator(PAYMENTS_MENU).count() > 0
        while not present and time.monotonic() < deadline:
            time.sleep(0.2)
            present = cp_frame.locator(PAYMENTS_MENU).count() > 0
        return present
    finally:
        cp_context.close()


def _fill_payment_form(cp_frame, email: str, first_name: str) -> None:
    email_field = cp_frame.locator(EMAIL_FIELD).first
    email_field.wait_for(state="visible", timeout=NAV_TIMEOUT)
    email_field.fill(email, timeout=UI_TIMEOUT)
    name_field = cp_frame.get_by_label("First Name")
    if name_field.count() == 0:
        name_field = cp_frame.locator("xpath=//label[contains(.,'First Name')]/../input")
    name_field.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    name_field.first.fill(first_name, timeout=UI_TIMEOUT)


def _attempt_payment_and_detect_error(page: Page, context: dict, *, pay_for, amount, email, first_name) -> bool:
    """One attempt to open the form, pay, and detect the no-payment error. Returns True if
    the error dialog was found. Raises PlaywrightTimeoutError on transient open/fill timeouts."""
    cp_page, cp_context = open_payment_form(page, context, pay_for=pay_for, amount=amount)
    try:
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        _fill_payment_form(cp_frame, email, first_name)

        checkout = cp_frame.get_by_role("button", name=CHECKOUT_BUTTON_RE).first
        checkout.wait_for(state="visible", timeout=UI_TIMEOUT)
        checkout.click(timeout=UI_TIMEOUT)

        proceed = cp_frame.locator(PROCEED_TO_PAYMENT)
        if proceed.count() > 0:
            try:
                proceed.first.click(timeout=UI_TIMEOUT)
            except Exception:
                pass

        deadline = time.monotonic() + NAV_TIMEOUT / 1000
        while time.monotonic() < deadline:
            if cp_frame.locator(ERROR_DIALOG).count() > 0:
                return True
            if cp_frame.get_by_text(NO_PAYMENT_TEXT).count() > 0:
                return True
            time.sleep(0.3)
        return False
    finally:
        cp_context.close()


def submit_payment_and_expect_error(
    page: Page, context: dict, *, pay_for: str, amount: str, email: str, first_name: str,
) -> None:
    """Open the make-payment form, attempt to pay, and assert the no-payment error dialog.

    With credit-card disabled (and only a card gateway connected) there is no available
    payment method, so the checkout surfaces an error dialog instead of a payment popup.
    The CP page load can transiently exceed the nav budget, so the open is retried.
    """
    last_timeout: Exception | None = None
    for attempt in range(FORM_OPEN_RETRIES + 1):
        try:
            if _attempt_payment_and_detect_error(
                page, context, pay_for=pay_for, amount=amount, email=email, first_name=first_name
            ):
                return
            raise AssertionError(
                "Expected a no-payment error dialog after attempting to pay with credit card "
                "disabled, but none appeared"
            )
        except PlaywrightTimeoutError as error:
            last_timeout = error
            continue
    raise AssertionError(
        f"Client-portal make-payment form did not load after {FORM_OPEN_RETRIES + 1} attempts: {last_timeout}"
    )
