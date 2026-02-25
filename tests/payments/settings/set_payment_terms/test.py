# Auto-generated from script.md
# Last updated: 2026-02-11
# Source: tests/payments/settings/set_payment_terms/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time
from playwright.sync_api import Page, expect

UI_TIMEOUT = 20000


def test_set_payment_terms(page: Page, context: dict) -> None:
    """
    Configure payment terms in Billing & Invoicing settings.

    Prerequisites:
    - User is logged in (from category _setup)

    Saves to context:
    - configured_payment_terms
    """
    if "/app/settings" not in page.url:
        settings_link = page.get_by_text("Settings", exact=True)
        settings_link.wait_for(state="visible", timeout=UI_TIMEOUT)
        settings_link.click()
        page.wait_for_url("**/app/settings", timeout=UI_TIMEOUT, wait_until="domcontentloaded")

    page.wait_for_load_state("domcontentloaded")
    settings_iframe_locator = page.locator('iframe[title="angularjs"]')
    if settings_iframe_locator.count() > 0:
        try:
            settings_iframe_locator.first.wait_for(state="visible", timeout=5000)
            settings_scope = page.frame_locator('iframe[title="angularjs"]')
        except Exception:
            settings_scope = page
    else:
        settings_scope = page

    if "/app/settings/billing_and_invoicing" not in page.url:
        billing_button = settings_scope.get_by_role("button", name="Set your invoices, estimates")
        billing_button.wait_for(state="visible", timeout=UI_TIMEOUT)
        billing_button.click()
        page.wait_for_url(
            "**/app/settings/billing_and_invoicing",
            timeout=UI_TIMEOUT,
            wait_until="domcontentloaded",
        )

    settings_iframe_locator = page.locator('iframe[title="angularjs"]')
    if settings_iframe_locator.count() > 0:
        try:
            settings_iframe_locator.first.wait_for(state="visible", timeout=5000)
            settings_scope = page.frame_locator('iframe[title="angularjs"]')
        except Exception:
            settings_scope = page
    else:
        settings_scope = page

    invoices_tab = settings_scope.get_by_role("tab", name=re.compile(r"^Invoices"))
    invoices_tab.wait_for(state="visible", timeout=UI_TIMEOUT)
    invoices_tab.scroll_into_view_if_needed()
    invoices_tab.click()

    due_on_receipt = settings_scope.get_by_role("radio", name="Due on receipt")
    due_on_receipt.wait_for(state="visible", timeout=UI_TIMEOUT)
    due_on_receipt.click()
    expect(due_on_receipt).to_be_checked()

    timestamp = int(time.time())
    payment_terms = f"Test payment terms {timestamp}"
    terms_box = settings_scope.get_by_role("textbox", name=re.compile("Terms & conditions")).first
    terms_box.wait_for(state="visible", timeout=10000)
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

    save_button = settings_scope.get_by_role("button", name="Save")
    expect(save_button).to_be_enabled()
    save_button.click()

    expect(terms_box).to_have_value(payment_terms)
    context["configured_payment_terms"] = payment_terms
