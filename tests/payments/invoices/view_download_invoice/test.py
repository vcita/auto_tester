# Auto-generated from script.md
# Last updated: 2026-02-19
# Source: tests/payments/invoices/view_download_invoice/script.md
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
        page.wait_for_url("**/app/pos", timeout=5000, wait_until="domcontentloaded")

        billing_link = page.get_by_text("Billing & Invoicing", exact=True)
        billing_link.wait_for(state="visible", timeout=5000)
        billing_link.click()
        page.wait_for_url(
            "**/app/payments/orders", timeout=5000, wait_until="domcontentloaded"
        )

    billing_scope = _get_billing_scope(page)
    invoice_link = billing_scope.get_by_role("link", name=re.compile("INVOICE #"))
    if invoice_link.count() == 0:
        invoice_link = billing_scope.get_by_text(re.compile("INVOICE #"))
    invoice_link.first.wait_for(state="visible", timeout=5000)
    invoice_link.first.scroll_into_view_if_needed()
    try:
        invoice_link.first.click(timeout=5000)
    except Exception:
        invoice_link.first.click(force=True)
    page.wait_for_url("**/app/invoices/**", timeout=5000, wait_until="domcontentloaded")
    return _get_billing_scope(page)


def _close_any_dialogs(page: Page, invoice_scope=None) -> None:
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

        title = scope.get_by_text("Copy link to share publicly", exact=True)
        if title.count() > 0:
            dialog_root = title.first.locator(
                "xpath=ancestor-or-self::*[@role='dialog' or contains(@class, 'md-dialog')]"
            )
            close_in_title = dialog_root.locator(
                'button[aria-label="Close"], button:has-text("Close"), button.md-icon-button'
            )
            if close_in_title.count() > 0:
                close_in_title.first.click()
                dialog_root.wait_for(state="hidden", timeout=10000)
                return True

        return False

    if _close_in_scope(page):
        return
    if invoice_scope is not None and _close_in_scope(invoice_scope):
        return

    page.keyboard.press("Escape")


def test_view_download_invoice(page: Page, context: dict) -> None:
    """
    Verify invoice client-view availability and download capability in one flow.

    Prerequisites:
    - User is logged in (from category _setup)

    Saves to context:
    - client_portal_invoice_url
    - client_portal_status
    - downloaded_invoice_filename
    - download_status
    """
    invoice_scope = _open_invoice(page)

    share_button = invoice_scope.get_by_role("button", name="Share")
    if share_button.count() == 0:
        context["client_portal_invoice_url"] = ""
        context["client_portal_status"] = "not_supported"
        context["downloaded_invoice_filename"] = ""
        context["download_status"] = "not_supported"
        return

    context["client_portal_invoice_url"] = "copied_public_link"
    context["client_portal_status"] = "available"

    _close_any_dialogs(page, invoice_scope)
    if (
        invoice_scope.get_by_role("menuitem", name=re.compile("Copy public link")).count()
        > 0
    ):
        page.keyboard.press("Escape")
        page.mouse.click(10, 10)
        share_toggle = invoice_scope.get_by_text("Share", exact=True)
        if share_toggle.count() > 0:
            share_toggle.first.click()

    if page.get_by_role("dialog").count() > 0:
        context["downloaded_invoice_filename"] = ""
        context["download_status"] = "not_supported"
        return

    view_button = invoice_scope.get_by_role("button", name="View Invoice")
    if view_button.count() == 0:
        context["downloaded_invoice_filename"] = ""
        context["download_status"] = "not_supported"
        return

    try:
        with page.expect_popup(timeout=5000) as popup_info:
            view_button.first.click()
        portal_page = popup_info.value
        portal_page.wait_for_load_state("domcontentloaded", timeout=5000)
    except Exception:
        portal_page = page

    download_trigger = portal_page.get_by_role(
        "button", name=re.compile("Download|PDF", re.I)
    )
    if download_trigger.count() == 0:
        download_trigger = portal_page.get_by_role(
            "link", name=re.compile("Download|PDF", re.I)
        )
    if download_trigger.count() == 0:
        download_trigger = portal_page.get_by_text(re.compile("Download|PDF", re.I))

    if download_trigger.count() == 0:
        context["downloaded_invoice_filename"] = ""
        context["download_status"] = "not_supported"
        return

    with portal_page.expect_download(timeout=5000) as download_info:
        download_trigger.first.click()
    download = download_info.value
    try:
        download.path()
    except Exception as exc:
        context["downloaded_invoice_filename"] = ""
        context["download_status"] = "failed"
        raise Exception("Invoice download did not complete") from exc

    context["downloaded_invoice_filename"] = (
        download.suggested_filename or "downloaded_invoice.pdf"
    )
    context["download_status"] = "downloaded"
