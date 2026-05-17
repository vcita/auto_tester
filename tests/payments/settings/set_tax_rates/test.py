# Auto-generated from script.md
# Last updated: 2026-02-11
# Source: tests/payments/settings/set_tax_rates/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time
from playwright.sync_api import Page, expect

UI_TIMEOUT = 20000


def test_set_tax_rates(page: Page, context: dict) -> None:
    """
    Configure tax rates in Billing & Invoicing settings and verify they are saved.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - configured_tax_name
    - configured_tax_rate
    """
    print("  Step 1: Ensure on Settings page...")
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

    # Step 2: Open Billing & Invoicing (only if not already there)
    print("  Step 2: Open Billing & Invoicing...")
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

    # Step 3: Open Taxes settings
    print("  Step 3: Open Taxes settings...")
    taxes_tab = settings_scope.get_by_role("tab", name=re.compile(r"^Taxes"))
    taxes_tab.wait_for(state="visible", timeout=UI_TIMEOUT)
    taxes_tab.scroll_into_view_if_needed()
    taxes_tab.click()

    # Step 4: Add new tax
    print("  Step 4: Wait for tax settings...")
    vue_iframe = settings_scope.locator("#vue-app-tab")
    if vue_iframe.count() > 0:
        taxes_scope = settings_scope.frame_locator("#vue-app-tab")
    else:
        taxes_scope = settings_scope

    taxes_scope.get_by_text("Tax settings", exact=True).wait_for(state="visible", timeout=UI_TIMEOUT)
    add_tax_button = taxes_scope.get_by_role("button", name="Add new tax")
    add_tax_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    add_tax_button.click()

    # Step 5: Enter tax name and rate
    timestamp = int(time.time())
    tax_name = f"Test Tax {timestamp}"
    tax_rate = "17"

    tax_name_input = taxes_scope.get_by_role("textbox", name="Tax name").last
    try:
        tax_name_input.wait_for(state="visible", timeout=5000)
    except Exception:
        add_tax_button.click()
        tax_name_input.wait_for(state="visible", timeout=5000)
    tax_name_input.click()
    tax_name_input.press_sequentially(tax_name, delay=30)

    tax_rate_input = taxes_scope.get_by_role("spinbutton", name="Tax rate").last
    tax_rate_input.wait_for(state="visible", timeout=10000)
    tax_rate_input.click()
    tax_rate_input.press_sequentially(tax_rate, delay=30)

    # Step 6: Save settings
    save_button = settings_scope.get_by_role("button", name="Save")
    expect(save_button).to_be_enabled()
    save_button.click()

    # Step 7: Verify tax values
    expect(tax_name_input).to_have_value(tax_name)
    expect(tax_rate_input).to_have_value(tax_rate)

    context["configured_tax_name"] = tax_name
    context["configured_tax_rate"] = tax_rate
