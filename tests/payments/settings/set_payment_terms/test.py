# Auto-generated from script.md
# Source: tests/payments/settings/set_payment_terms/script.md

import re
import time
from playwright.sync_api import Page, expect

UI_TIMEOUT = 20000
BILLING_URL_GLOB = "**/app/settings/billing_and_invoicing"
TERMS_NAME = re.compile("Terms & conditions")


def test_set_payment_terms(page: Page, context: dict) -> None:
    """
    Configure payment terms in Billing & Invoicing settings.

    Prerequisites:
    - User is logged in (from category _setup)

    Saves to context:
    - configured_payment_terms
    """
    _navigate_to_billing_invoices(page)

    timestamp = int(time.time())
    payment_terms = f"Test payment terms {timestamp}"

    # The billing form lives in a child-app frame whose identity differs across the Vue
    # and legacy Angular billing UIs, so the form frame is resolved dynamically and the
    # whole interaction happens inside it. A reload between attempts re-mounts the form.
    form, terms_box = _prepare_invoice_terms_field(page)

    terms_box.click()
    terms_box.fill(payment_terms)
    if terms_box.input_value().strip() != payment_terms:
        terms_box.click()
        try:
            page.keyboard.press("Control+A")
        except Exception:
            page.keyboard.press("Meta+A")
        terms_box.fill("")
        terms_box.press_sequentially(payment_terms, delay=30)

    save_button = form.get_by_role("button", name="Save").first
    expect(save_button).to_be_enabled()
    save_button.click()

    expect(terms_box).to_have_value(payment_terms)
    context["configured_payment_terms"] = payment_terms


def _navigate_to_billing_invoices(page: Page) -> None:
    if "/app/settings" not in page.url:
        settings_link = page.get_by_text("Settings", exact=True)
        settings_link.wait_for(state="visible", timeout=UI_TIMEOUT)
        settings_link.click()
        page.wait_for_url("**/app/settings", timeout=UI_TIMEOUT, wait_until="domcontentloaded")

    if "/app/settings/billing_and_invoicing" not in page.url:
        scope = _settings_scope(page)
        billing_button = scope.get_by_role("button", name="Set your invoices, estimates")
        billing_button.wait_for(state="visible", timeout=UI_TIMEOUT)
        billing_button.click()
        page.wait_for_url(BILLING_URL_GLOB, timeout=UI_TIMEOUT, wait_until="domcontentloaded")


def _prepare_invoice_terms_field(page: Page):
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            _click_invoices_tab(page)
            form = _billing_form_frame(page)
            due_on_receipt = form.get_by_role("radio", name="Due on receipt").first
            due_on_receipt.wait_for(state="visible", timeout=UI_TIMEOUT)
            due_on_receipt.click()
            expect(due_on_receipt).to_be_checked()
            return form, _wait_for_terms_box(form)
        except Exception as error:  # noqa: BLE001 - retried by reloading the form
            last_error = error
            if attempt == 2:
                break
            page.reload(wait_until="domcontentloaded")
            page.wait_for_url(BILLING_URL_GLOB, timeout=UI_TIMEOUT, wait_until="domcontentloaded")
    raise AssertionError(f"Invoice Terms & conditions field never became ready: {last_error}")


def _click_invoices_tab(page: Page) -> None:
    deadline = time.time() + UI_TIMEOUT / 1000
    while time.time() < deadline:
        for frame in page.frames:
            tab = frame.get_by_role("tab", name=re.compile(r"^Invoices")).first
            try:
                if tab.count() and tab.is_visible():
                    tab.scroll_into_view_if_needed()
                    tab.click()
                    return
            except Exception:  # noqa: BLE001 - frame may navigate mid-poll
                pass
        time.sleep(0.3)
    raise AssertionError("Invoices & Estimates tab not found")


def _billing_form_frame(page: Page):
    """Return the frame that actually hosts the billing form (the 'Due on receipt' radio).

    The form renders inside a child-app frame that is not always the angularjs iframe, so
    it is identified by the control that is unique to this settings page.
    """
    deadline = time.time() + UI_TIMEOUT / 1000
    while time.time() < deadline:
        for frame in page.frames:
            radio = frame.get_by_role("radio", name="Due on receipt").first
            try:
                if radio.count() and radio.is_visible():
                    return frame
            except Exception:  # noqa: BLE001 - frame may navigate mid-poll
                pass
        time.sleep(0.3)
    raise AssertionError("Billing form frame ('Due on receipt') not found")


def _wait_for_terms_box(form, timeout_ms: int = 10000):
    """Return the invoice Terms & conditions field across both billing UIs.

    The Vue billing UI exposes an accessible "Terms & conditions" textbox. The legacy
    Angular UI renders terms as md-input textareas with no accessible name; the invoice
    terms is the first ".explicit-overflow" textarea (estimate terms is second).
    TODO(app): add a stable data-qa to the invoice terms field to drop the CSS fallback.
    """
    vue_box = form.get_by_role("textbox", name=TERMS_NAME).first
    angular_box = form.locator("textarea.explicit-overflow").first
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        for box in (vue_box, angular_box):
            try:
                if box.count() and box.is_visible():
                    return box
            except Exception:  # noqa: BLE001 - locator may resolve mid-render
                pass
        time.sleep(0.3)
    raise AssertionError("Terms & conditions field not found in either billing UI variant")


def _settings_scope(page: Page):
    iframe = page.locator('iframe[title="angularjs"]')
    if iframe.count() > 0:
        try:
            iframe.first.wait_for(state="visible", timeout=5000)
            return page.frame_locator('iframe[title="angularjs"]')
        except Exception:
            return page
    return page
