# Auto-generated from script.md
# Last updated: 2026-02-11
# Source: tests/payments/settings/set_tax_rates/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time
from playwright.sync_api import Page, expect

UI_TIMEOUT = 20000


def _first_visible_locator(locators, timeout: int = UI_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for locator in locators:
            for index in range(locator.count()):
                candidate = locator.nth(index)
                try:
                    if candidate.is_visible():
                        return candidate
                except Exception:
                    continue
        time.sleep(0.1)
    return None


def _confirm_apply_default_tax_to_existing_items(
    page: Page, settings_scope, taxes_scope
) -> None:
    scopes = (page, taxes_scope, settings_scope)
    dialog_title = _first_visible_locator(
        [
            scope.get_by_text("Confirm default taxes", exact=True)
            for scope in scopes
        ],
        timeout=5000,
    )
    if dialog_title is None:
        raise AssertionError("Confirm default taxes dialog did not appear")

    existing_items_checkbox = _first_visible_locator(
        [
            scope.locator("label, .v-input").filter(
                has_text=re.compile(r"Also apply to existing items", re.I)
            )
            for scope in scopes
        ],
        timeout=5000,
    )
    if existing_items_checkbox is None:
        raise AssertionError("Apply-to-existing-items checkbox did not appear")

    if not _is_checkbox_label_checked(existing_items_checkbox):
        existing_items_checkbox.click(force=True)
    _assert_checkbox_label_checked(existing_items_checkbox)

    confirm_button = _first_visible_locator(
        [
            scope.get_by_role("button", name="Confirm")
            for scope in scopes
        ],
        timeout=5000,
    )
    if confirm_button is None:
        raise AssertionError("Confirm default taxes button did not appear")

    confirm_button.click()
    dialog_title.wait_for(state="hidden", timeout=5000)


def _assert_checkbox_label_checked(label_locator) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if _is_checkbox_label_checked(label_locator):
            return
        time.sleep(0.1)
    raise AssertionError(
        "Default tax confirmation checkbox was not checked before confirming"
    )


def _save_tax_settings(page: Page, settings_scope, taxes_scope) -> None:
    save_button = settings_scope.get_by_role("button", name="Save")
    save_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    expect(save_button).to_be_enabled(timeout=UI_TIMEOUT)
    save_button.click(force=True)

    _confirm_apply_default_tax_to_existing_items(page, settings_scope, taxes_scope)

    try:
        expect(save_button).to_be_disabled(timeout=2000)
    except Exception:
        pass
    expect(save_button).to_be_enabled(timeout=UI_TIMEOUT)


def _is_checkbox_label_checked(label_locator) -> bool:
    return bool(
        label_locator.evaluate(
            """label => {
                const control = label.closest('.v-input') || label.parentElement;
                if (!control) return false;

                const input = control.querySelector('input[type="checkbox"]');
                if (input?.checked || input?.getAttribute('aria-checked') === 'true') {
                    return true;
                }

                const className = `${control.className || ''} ${label.className || ''}`;
                return className.includes('v-input--is-label-active')
                    || !!control.querySelector('.mdi-checkbox-marked, .primary--text, .accent--text');
            }"""
        )
    )


def _apply_tax_to_all(taxes_scope) -> None:
    apply_dropdown = taxes_scope.get_by_text("Apply default tax to", exact=True).last
    apply_dropdown.wait_for(state="visible", timeout=10000)
    apply_dropdown.click()

    select_all_row = taxes_scope.locator("label").filter(has_text="Select All").last
    if select_all_row.count() == 0:
        select_all_row = taxes_scope.get_by_text("Select All", exact=True).last
    select_all_row.wait_for(state="visible", timeout=5000)
    select_all_row.click(force=True)

    _assert_tax_applied_to_all(taxes_scope)


def _assert_tax_applied_to_all(taxes_scope) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if all(_is_tax_target_checked(taxes_scope, option) for option in _tax_target_options()):
            return
        time.sleep(0.1)
    raise AssertionError("Tax was not applied to all target types")


def _is_tax_target_checked(taxes_scope, option: str) -> bool:
    option_row = taxes_scope.locator("label").filter(has_text=option).last
    if option_row.count() == 0:
        return False

    return bool(
        option_row.evaluate(
            """label => {
                const control = label.closest('.v-input') || label.parentElement;
                if (!control) return false;

                const input = control.querySelector('input[type="checkbox"]');
                if (input?.checked || input?.getAttribute('aria-checked') === 'true') {
                    return true;
                }

                const className = `${control.className || ''} ${label.className || ''}`;
                return className.includes('v-input--is-label-active')
                    || !!control.querySelector('.mdi-checkbox-marked, .primary--text, .accent--text');
            }"""
        )
    )


def _tax_target_options() -> tuple[str, str, str]:
    return ("Services", "Products", "Packages")


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

    add_tax_button = taxes_scope.get_by_role("button", name="Add new tax")
    try:
        add_tax_button.wait_for(state="visible", timeout=8000)
    except Exception:
        taxes_scope.get_by_text("Tax settings", exact=True).wait_for(
            state="visible", timeout=5000
        )
        add_tax_button.wait_for(state="visible", timeout=5000)
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
    tax_rate_input.fill(tax_rate)

    # Step 6: Apply tax to all supported item types
    print("  Step 6: Apply tax to all item types...")
    _apply_tax_to_all(taxes_scope)

    # Step 7: Save settings
    print("  Step 7: Save tax settings...")
    _save_tax_settings(page, settings_scope, taxes_scope)

    # Step 8: Verify tax values
    expect(tax_name_input).to_have_value(tax_name)
    expect(tax_rate_input).to_have_value(tax_rate)

    context["configured_tax_name"] = tax_name
    context["configured_tax_rate"] = tax_rate
