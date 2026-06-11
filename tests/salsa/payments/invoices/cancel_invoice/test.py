# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/invoices/cancel_invoice/script.md
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


def _open_invoice(page: Page):
    if "/app/invoices/" in page.url:
        return _get_billing_scope(page)

    if "/app/payments/orders" not in page.url:
        sales_button = page.locator('[data-qa="nav-sales"]')
        if sales_button.count() == 0:
            sales_button = page.get_by_role("button", name="Sales", exact=True).first
        else:
            sales_button = sales_button.first
        sales_button.wait_for(state="visible", timeout=5000)
        sales_button.click()
        page.wait_for_url("**/app/pos**", timeout=5000, wait_until="domcontentloaded")

        billing_link = page.get_by_text("Billing & Invoicing", exact=True)
        billing_link.wait_for(state="visible", timeout=5000)
        billing_link.click()
        page.wait_for_url("**/app/payments/orders", timeout=5000, wait_until="domcontentloaded")

    billing_scope = _get_billing_scope(page)
    invoice_link = billing_scope.get_by_role("link", name=re.compile("INVOICE #")).first
    invoice_link.wait_for(state="visible", timeout=5000)
    invoice_link.click()
    page.wait_for_url("**/app/invoices/**", timeout=5000, wait_until="domcontentloaded")
    return _get_billing_scope(page)


def _click_actions_menu(invoice_scope) -> None:
    actions_button = invoice_scope.locator(
        'button:has-text("COPY INVOICE") + md-menu button'
    )
    if actions_button.count() == 0:
        actions_button = invoice_scope.locator(
            'button:has-text("COPY INVOICE") ~ md-menu button'
        )
    if actions_button.count() == 0:
        actions_button = invoice_scope.locator(
            'button:has-text("SEND REMINDER") + md-menu button'
        )
    if actions_button.count() == 0:
        actions_button = invoice_scope.locator(
            'button:has-text("SEND REMINDER") ~ md-menu button'
        )
    if actions_button.count() == 0:
        actions_button = _top_action_overflow_button(invoice_scope)

    actions_button.first.wait_for(state="visible", timeout=5000)
    actions_button.first.click()


def _top_action_overflow_button(invoice_scope):
    controls = invoice_scope.locator("button, a[ng-click]")
    for index in range(controls.count()):
        control = controls.nth(index)
        try:
            if not control.is_visible():
                continue
            text = control.inner_text().strip().lower()
            box = control.bounding_box()
            if not box or box["y"] > 400 or box["x"] > 900:
                continue
            if text in {"", "...", "more_horiz", "more_vert"}:
                return control
        except Exception:
            continue
    raise AssertionError("Top invoice actions menu button was not found")


def test_cancel_invoice(page: Page, context: dict) -> None:
    """
    Cancel an invoice and capture the status.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - canceled_invoice_status
    """
    invoice_scope = _open_invoice(page)
    if context.get("recorded_invoice_payment_status") == "recorded":
        context["canceled_invoice_status"] = "not_cancelable_after_payment"
        return

    _click_actions_menu(invoice_scope)

    cancel_item = invoice_scope.get_by_role("menuitem", name="Cancel invoice")
    cancel_item.wait_for(state="visible", timeout=5000)
    cancel_item.click()

    dialog = invoice_scope.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=5000)
    confirm = dialog.get_by_role(
        "button", name=re.compile(r"^(Confirm|Yes|Cancel invoice|Void invoice)$", re.I)
    )
    if confirm.count() == 0:
        raise Exception("Cancel confirmation action was not found")
    confirm.first.click()

    canceled_text = invoice_scope.get_by_text("Cancelled", exact=False)
    canceled_status = "cancelled" if canceled_text.count() > 0 else "unknown"
    context["canceled_invoice_status"] = canceled_status

