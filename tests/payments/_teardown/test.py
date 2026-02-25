# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/_teardown/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re

from playwright.sync_api import Page


def _get_billing_scope(page: Page):
    billing_iframe = page.locator('iframe[title="angularjs"]')
    if billing_iframe.count() > 0:
        try:
            billing_iframe.first.wait_for(state="visible", timeout=5000)
            return page.frame_locator('iframe[title="angularjs"]')
        except Exception:
            return page
    return page


def _open_billing(page: Page):
    if "/app/payments/orders" in page.url:
        return _get_billing_scope(page)

    sales_button = page.get_by_role("button", name="Sales")
    sales_button.wait_for(state="visible", timeout=45000)
    sales_button.click()
    page.wait_for_url("**/app/pos", timeout=45000, wait_until="domcontentloaded")

    billing_link = page.get_by_text("Billing & Invoicing", exact=True)
    billing_link.wait_for(state="visible", timeout=45000)
    billing_link.click()
    page.wait_for_url("**/app/payments/orders", timeout=45000, wait_until="domcontentloaded")
    return _get_billing_scope(page)


def _close_any_dialogs(page: Page, billing_scope=None) -> None:
    def _close_in_scope(scope) -> bool:
        dialog = scope.get_by_role("dialog")
        if dialog.count() > 0:
            close_button = dialog.first.get_by_role(
                "button", name=re.compile("Close|×|X", re.I)
            )
            if close_button.count() > 0:
                close_button.first.click()
                dialog.first.wait_for(state="hidden", timeout=10000)
                return True
            aria_close = dialog.first.locator('button[aria-label="Close"]')
            if aria_close.count() > 0:
                aria_close.first.click()
                dialog.first.wait_for(state="hidden", timeout=10000)
                return True

        md_dialog = scope.locator("md-dialog")
        if md_dialog.count() > 0:
            md_close = md_dialog.first.locator(
                'button[aria-label="Close"], button[ng-click*="cancel"], button.md-icon-button'
            )
            if md_close.count() > 0:
                md_close.first.click()
                md_dialog.first.wait_for(state="hidden", timeout=10000)
                return True
        return False

    if _close_in_scope(page):
        return
    if billing_scope is not None and _close_in_scope(billing_scope):
        return
    page.keyboard.press("Escape")


def _cancel_invoice(page: Page, billing_scope, invoice_id: str) -> None:
    invoice_link = billing_scope.locator(f'a[href*="{invoice_id}"]')
    if invoice_link.count() == 0:
        return

    invoice_link.first.click()
    page.wait_for_url("**/app/invoices/**", timeout=45000, wait_until="domcontentloaded")
    invoice_scope = _get_billing_scope(page)

    menu_button = invoice_scope.locator("md-menu").filter(
        has_text=re.compile("Edit")
    ).get_by_role("button")
    if menu_button.count() == 0:
        return

    menu_button.first.click()
    cancel_item = invoice_scope.get_by_role("menuitem", name="Cancel invoice")
    if cancel_item.count() == 0:
        return

    cancel_item.first.click()
    dialog = invoice_scope.get_by_role("dialog")
    confirm = dialog.get_by_role(
        "button", name=re.compile(r"^(Confirm|Yes|Cancel invoice|Void invoice)$", re.I)
    )
    if confirm.count() > 0:
        confirm.first.click()


def teardown_payments(page: Page, context: dict) -> None:
    """
    Cancel test invoices when possible and clear context keys.
    """
    invoice_id = context.get("created_invoice_id")
    if not invoice_id:
        keys_to_clear = [
            key
            for key in list(context.keys())
            if key.startswith(("created_", "recorded_", "configured_", "issued_"))
        ]
        for key in keys_to_clear:
            context.pop(key, None)
        return

    _close_any_dialogs(page)
    billing_scope = _open_billing(page)
    _close_any_dialogs(page, billing_scope)
    _cancel_invoice(page, billing_scope, invoice_id)

    keys_to_clear = [
        key
        for key in list(context.keys())
        if key.startswith(("created_", "recorded_", "configured_", "issued_"))
    ]
    for key in keys_to_clear:
        context.pop(key, None)

