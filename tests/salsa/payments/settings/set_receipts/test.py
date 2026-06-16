# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/settings/set_receipts/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re

from playwright.sync_api import Page, expect

UI_TIMEOUT = 20000


def _get_settings_scope(page: Page):
    settings_iframe = page.locator('iframe[title="angularjs"]')
    if settings_iframe.count() > 0:
        try:
            settings_iframe.first.wait_for(state="visible", timeout=5000)
            return page.frame_locator('iframe[title="angularjs"]')
        except Exception:
            return page
    return page


def test_set_receipts(page: Page, context: dict) -> None:
    """
    Configure receipt settings when available without a gateway.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - configured_receipt_settings
    """
    if "/app/settings" not in page.url:
        settings_link = page.get_by_text("Settings", exact=True)
        settings_link.wait_for(state="visible", timeout=UI_TIMEOUT)
        settings_link.click()
        page.wait_for_url("**/app/settings", timeout=UI_TIMEOUT, wait_until="domcontentloaded")

    settings_scope = _get_settings_scope(page)

    if "/app/settings/payments" not in page.url:
        payments_button = settings_scope.get_by_role(
            "button", name="Connect your preferred payment provider"
        )
        if payments_button.count() == 0:
            context["configured_receipt_settings"] = "unavailable_without_gateway"
            return
        payments_button.first.click()
        page.wait_for_url("**/app/settings/payments", timeout=UI_TIMEOUT, wait_until="domcontentloaded")

    settings_scope = _get_settings_scope(page)
    terms_tab = settings_scope.get_by_text("Terms & Policies", exact=True)
    if terms_tab.count() == 0:
        context["configured_receipt_settings"] = "unavailable_without_gateway"
        return
    terms_tab.first.click()

    receipt_checkboxes = settings_scope.get_by_role(
        "checkbox", name=re.compile("receipt", re.I)
    )
    receipt_text = settings_scope.get_by_text("receipt", exact=False)

    if receipt_checkboxes.count() == 0 and receipt_text.count() == 0:
        context["configured_receipt_settings"] = "unavailable_without_gateway"
        return

    updated = False
    if receipt_checkboxes.count() > 0:
        checkbox = receipt_checkboxes.first
        if checkbox.is_enabled():
            checkbox.click()
            updated = True

    save_button = settings_scope.get_by_role("button", name="Save")
    if updated:
        expect(save_button).to_be_enabled()
        save_button.click()

    context["configured_receipt_settings"] = (
        "updated" if updated else "available_not_editable"
    )

