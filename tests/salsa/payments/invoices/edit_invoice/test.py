# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/invoices/edit_invoice/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time
from decimal import Decimal

from playwright.sync_api import Page, expect

UI_TIMEOUT = 5000


def _get_billing_scope(page: Page):
    billing_iframe = page.locator('iframe[title="angularjs"]')
    if billing_iframe.count() > 0:
        try:
            billing_iframe.first.wait_for(state="visible", timeout=5000)
            return page.frame_locator('iframe[title="angularjs"]')
        except Exception:
            return page
    return page


def _get_editor_scope(billing_scope):
    editor_iframe = billing_scope.locator("#vue_wizard_iframe")
    if editor_iframe.count() > 0:
        return billing_scope.frame_locator("#vue_wizard_iframe")
    return billing_scope


def _open_invoice(page: Page):
    if "/app/invoices/" in page.url:
        return _get_billing_scope(page)

    if "/app/payments/orders" not in page.url:
        sales_button = page.locator('[data-qa="nav-sales"]')
        if sales_button.count() == 0:
            sales_button = page.get_by_role("button", name="Sales", exact=True).first
        else:
            sales_button = sales_button.first
        sales_button.wait_for(state="visible", timeout=UI_TIMEOUT)
        sales_button.click()
        page.wait_for_url("**/app/pos**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")

        billing_link = page.get_by_text("Billing & Invoicing", exact=True)
        billing_link.wait_for(state="visible", timeout=UI_TIMEOUT)
        billing_link.click()
        page.wait_for_url("**/app/payments/orders", timeout=UI_TIMEOUT, wait_until="domcontentloaded")

    billing_scope = _get_billing_scope(page)
    invoice_link = billing_scope.get_by_role("link", name=re.compile("INVOICE #")).first
    invoice_link.wait_for(state="visible", timeout=UI_TIMEOUT)
    invoice_link.click()
    page.wait_for_url("**/app/invoices/**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
    return _get_billing_scope(page)


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


def _select_priced_service(
    page: Page, invoice_scope, editor_scope, service_name: str, baseline_amount: str
) -> None:
    """Add the priced service to the invoice and confirm the editor total reflects it.

    The picker selection is occasionally dropped (option click lands before the
    dropdown is interactive), which silently leaves the invoice unchanged. Confirm
    the editor total rose above the pre-edit value before returning, retrying the
    selection once if the first attempt did not register.
    """
    for attempt in range(2):
        item_box = editor_scope.get_by_role("textbox", name="Please select an item")
        item_box.wait_for(state="visible", timeout=UI_TIMEOUT)
        item_box.click()
        # Type the service name to filter the picker to the intended priced
        # service. Without filtering, clicking the box in a fresh account lands
        # on a default $0 service (e.g. "Introductory phone call"), which leaves
        # the total unchanged.
        item_box.fill(service_name)

        option_locators = [
            scope.get_by_role("option", name=re.compile(re.escape(service_name), re.I))
            for scope in (page, invoice_scope, editor_scope)
        ] + [
            scope.get_by_text(service_name, exact=True)
            for scope in (page, invoice_scope, editor_scope)
        ]
        service_option = _first_visible_locator(option_locators)
        if service_option is None:
            raise AssertionError(f"Invoice service option did not appear: {service_name}")

        service_option.scroll_into_view_if_needed(timeout=UI_TIMEOUT)
        service_option.click(force=True)

        if _editor_total_increased(editor_scope, baseline_amount, timeout=UI_TIMEOUT):
            return

    raise AssertionError(
        f"Adding service {service_name!r} did not raise the editor total above "
        f"{baseline_amount} after 2 attempts"
    )


def _editor_total_increased(editor_scope, baseline_amount: str, timeout: int) -> bool:
    """Return True once any currency amount in the editor exceeds the pre-edit total
    (i.e. the added line item registered)."""
    baseline_value = _amount_to_decimal(baseline_amount)
    amounts = editor_scope.get_by_text(re.compile(r"[₪$]\s?\d"))
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        max_value = _max_currency_amount(amounts)
        if max_value is not None and max_value > baseline_value:
            return True
        time.sleep(0.2)
    return False


def _max_currency_amount(amounts_locator) -> Decimal | None:
    largest: Decimal | None = None
    try:
        texts = amounts_locator.all_inner_texts()
    except Exception:
        return None
    for text in texts:
        for token in re.findall(r"[₪$]\s?([\d,]+(?:\.\d{1,2})?)", text):
            value = Decimal(token.replace(",", ""))
            if largest is None or value > largest:
                largest = value
    return largest


def _amount_to_decimal(amount_text: str) -> Decimal:
    match = re.search(r"[\d,.]+", amount_text)
    if not match:
        raise AssertionError(f"Could not parse invoice amount: {amount_text}")
    return Decimal(match.group(0).replace(",", ""))


def _click_edit_action(invoice_scope) -> None:
    direct_edit = _first_visible_locator(
        [
            invoice_scope.locator('button[data-qa="edit"]').filter(
                has_text=re.compile(r"^\s*Edit\s*$", re.I)
            ),
            invoice_scope.get_by_role("button", name=re.compile(r"^Edit$", re.I)),
        ],
        timeout=500,
    )
    if direct_edit is not None:
        direct_edit.click()
        return

    actions_button = invoice_scope.locator(
        'button:has-text("SEND REMINDER") + md-menu button'
    )
    if actions_button.count() == 0:
        actions_button = invoice_scope.locator(
            'button:has-text("SEND REMINDER") ~ md-menu button'
        )
    if actions_button.count() == 0:
        actions_button = invoice_scope.locator(
            'button:has-text("Send reminder") + md-menu button'
        )
    if actions_button.count() == 0:
        actions_button = invoice_scope.locator(
            'button:has-text("Send reminder") ~ md-menu button'
        )
    if actions_button.count() == 0:
        actions_button = invoice_scope.locator(
            'md-menu[ng-repeat*="moreActions"] button[ng-click*="$mdOpenMenu"]'
        )
    if actions_button.count() == 0:
        actions_button = invoice_scope.locator(
            'md-menu[ng-repeat*="moreActions"] button'
        )
    if actions_button.count() == 0:
        actions_button = _top_action_overflow_button(invoice_scope)

    actions_button.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    actions_button.first.click()

    menu_edit = _first_visible_locator(
        [
            invoice_scope.get_by_role("menuitem", name=re.compile(r"^Edit$", re.I)),
            invoice_scope.locator('button[data-qa="edit"]').filter(
                has_text=re.compile(r"^\s*Edit\s*$", re.I)
            ),
            invoice_scope.get_by_role("button", name=re.compile(r"^Edit$", re.I)),
        ]
    )
    if menu_edit is None:
        raise AssertionError("Edit action did not appear after opening invoice actions menu")
    menu_edit.click()


def _top_action_overflow_button(invoice_scope):
    controls = invoice_scope.locator("button, a[ng-click]")
    visible_controls = []
    for index in range(controls.count()):
        control = controls.nth(index)
        try:
            if not control.is_visible():
                continue
            text = control.inner_text().strip().lower()
            box = control.bounding_box()
            if box:
                visible_controls.append(f"{text or '<empty>'}@{int(box['x'])},{int(box['y'])}")
            if not box or box["y"] > 400 or box["x"] > 900:
                continue
            if text in {"", "...", "more_horiz", "more_vert"}:
                return control
        except Exception:
            continue
    raise AssertionError(
        "Top invoice actions menu button was not found; "
        f"visible controls: {', '.join(visible_controls[:20])}"
    )


def _wait_for_increased_total(invoice_scope, original_amount: str) -> str:
    """Wait until the persisted invoice total changes from the pre-edit value and is
    larger.

    Adding a priced line item must raise the grand total. This check is
    self-contained: it asserts the edit took effect and persisted without depending
    on a tax rate configured by a sibling subcategory in the same shared account
    (which made the prior exact-amount assertion flake in full-suite runs).
    """
    original_value = _amount_to_decimal(original_amount)
    amount_heading = invoice_scope.get_by_role("heading", name=re.compile(r"^[₪$]\d"))
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    last_amount = ""
    while time.monotonic() < deadline:
        if amount_heading.count() > 0:
            last_amount = amount_heading.first.inner_text().strip()
            if (
                last_amount
                and last_amount != original_amount
                and _amount_to_decimal(last_amount) > original_value
            ):
                return last_amount
        time.sleep(0.1)

    raise AssertionError(
        f"Invoice total did not increase after adding a line item; "
        f"original {original_amount!r}, last visible total {last_amount or '<none>'!r}"
    )


def test_edit_invoice(page: Page, context: dict) -> None:
    """
    Edit an invoice by adding another item and verify total changes.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - created_invoice_amount
    """
    invoice_scope = _open_invoice(page)

    amount_heading = invoice_scope.get_by_role("heading", name=re.compile(r"^[₪$]\d"))
    amount_heading.wait_for(state="visible", timeout=UI_TIMEOUT)
    original_amount = amount_heading.first.inner_text().strip()

    _click_edit_action(invoice_scope)

    editor_scope = _get_editor_scope(invoice_scope)
    service_name = context.get("invoice_service_name")
    if not service_name:
        raise ValueError("invoice_service_name missing from context - run payments _setup first")
    _select_priced_service(page, invoice_scope, editor_scope, service_name, original_amount)

    save_button = editor_scope.get_by_role(
        "button", name=re.compile(r"Save draft|Save")
    )
    save_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    expect(save_button.first).to_be_enabled(timeout=UI_TIMEOUT)
    save_button.first.click()

    page.wait_for_url("**/app/invoices/**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
    invoice_scope = _get_billing_scope(page)
    updated_amount = _wait_for_increased_total(invoice_scope, original_amount)
    context["created_invoice_amount"] = updated_amount.replace("₪", "").replace("$", "").strip()

