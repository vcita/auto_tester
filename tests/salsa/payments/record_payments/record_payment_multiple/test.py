# Auto-generated from script.md
# Last updated: 2026-02-12
# Source: tests/payments/record_payments/record_payment_multiple/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time
from decimal import Decimal

from playwright.sync_api import Page, expect
from tests.salsa.payments.invoices.create_invoice.test import (
    test_create_invoice as _create_invoice_for_payment,
)


def _get_billing_scope(page: Page):
    billing_iframe = page.locator('iframe[title="angularjs"]')
    if billing_iframe.count() > 0:
        try:
            billing_iframe.first.wait_for(state="visible", timeout=5000)
            return page.frame_locator('iframe[title="angularjs"]')
        except Exception:
            return page
    return page


def _open_invoice(page: Page, context: dict):
    if "/app/invoices/" in page.url:
        return _get_billing_scope(page)

    if "/app/payments/orders" not in page.url:
        billing_link = page.get_by_text("Billing & Invoicing", exact=True)
        if billing_link.count() > 0 and billing_link.first.is_visible():
            billing_link.first.click()
        else:
            sales_button = page.locator('[data-qa="nav-sales"]')
            if sales_button.count() == 0:
                sales_button = page.get_by_role("button", name="Sales", exact=True).first
            else:
                sales_button = sales_button.first
            sales_button.wait_for(state="visible", timeout=5000)
            sales_button.click()
            billing_link = page.get_by_text("Billing & Invoicing", exact=True)
        billing_link.wait_for(state="visible", timeout=5000)
        billing_link.click()
        page.wait_for_url("**/app/payments/orders", timeout=5000, wait_until="domcontentloaded")

    billing_scope = _get_billing_scope(page)
    invoice_link = billing_scope.get_by_role("link", name=re.compile("INVOICE #")).first
    if invoice_link.count() == 0:
        _create_invoice_for_payment(page, context)
        return _get_billing_scope(page)

    invoice_link.wait_for(state="visible", timeout=5000)
    invoice_link.click()
    page.wait_for_url("**/app/invoices/**", timeout=5000, wait_until="domcontentloaded")
    return _get_billing_scope(page)


def _first_visible_locator(locators, timeout: int = 5000):
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


def _open_record_payment_dialog(page: Page, invoice_scope):
    for attempt in range(4):
        take_payment = invoice_scope.get_by_role(
            "button", name=re.compile(r"^Take payment")
        ).first
        try:
            take_payment.wait_for(state="visible", timeout=5000)
            take_payment.scroll_into_view_if_needed(timeout=5000)
            if attempt == 0:
                take_payment.click(force=True)
            else:
                take_payment.evaluate("(element) => element.click()")

            record_payment = _first_visible_locator(
                [
                    page.get_by_role("menuitem", name=re.compile("Record payment")),
                    invoice_scope.get_by_role("menuitem", name=re.compile("Record payment")),
                    page.get_by_text("Record payment", exact=True),
                    invoice_scope.get_by_text("Record payment", exact=True),
                ],
                timeout=2000,
            )
            if record_payment is not None:
                record_payment.click(force=True)
                dialog = invoice_scope.get_by_role("dialog", name=re.compile("Record payment"))
                dialog.wait_for(state="visible", timeout=5000)
                return dialog
        except Exception:
            continue

    raise AssertionError("Record payment action did not appear after opening Take payment")


def _find_amount_input(dialog):
    amount_input = dialog.locator(
        "input.amount-input:visible, input[name='money_amount']:visible"
    ).first
    if amount_input.count() > 0:
        return amount_input

    textboxes = dialog.get_by_role("textbox")
    for i in range(textboxes.count()):
        box = textboxes.nth(i)
        try:
            value = box.input_value()
        except Exception:
            continue
        if re.match(r"^\d+(\.\d+)?$", value):
            return box
    return textboxes.first


def _fill_payment_amount(dialog, amount_input, amount: str) -> None:
    amount_input.wait_for(state="visible", timeout=5000)

    amount_input.click()
    amount_input.press("Meta+A")
    amount_input.press("Backspace")
    amount_input.press_sequentially(amount, delay=50)
    amount_input.press("Tab")


def _commit_payment_amount(dialog, amount_input) -> None:
    reference_field = dialog.get_by_placeholder("Reference")
    if reference_field.count() > 0:
        reference_field.first.click()
    else:
        dialog.get_by_text("Payment details:", exact=True).click()
    amount_input.evaluate("(element) => element.blur()")


def _assert_recordable_amount(dialog, amount_input, amount: str) -> None:
    expected_total = dialog.get_by_text(
        re.compile(rf"Total:\s*\${re.escape(amount)}\.00")
    )
    expect(expected_total.first).to_be_visible(timeout=5000)

    validation = dialog.get_by_text(re.compile(r"Must be lower than", re.I))
    if validation.count() > 0:
        expect(validation.first).to_be_hidden(timeout=5000)

    record_button = dialog.get_by_role("button", name="Record")
    expect(record_button).to_be_enabled(timeout=5000)

    raw_value = amount_input.input_value()
    if amount not in raw_value:
        raise AssertionError(f"Payment amount was not set to {amount}: {raw_value}")


def _select_cash_method(invoice_scope, dialog) -> None:
    method_listbox = dialog.get_by_role("listbox", name="Payment received via")
    method_listbox.wait_for(state="visible", timeout=5000)
    if "Cash" in method_listbox.inner_text():
        return

    method_listbox.click()
    invoice_scope.get_by_role("option", name="Cash").click()


def _invoice_total_amount(invoice_scope) -> Decimal:
    amount_heading = invoice_scope.get_by_role("heading", name=re.compile(r"^[₪$]\d"))
    amount_heading.wait_for(state="visible", timeout=5000)
    amount_text = amount_heading.first.inner_text()
    match = re.search(r"[\d,.]+", amount_text)
    if not match:
        raise AssertionError(f"Could not parse invoice total: {amount_text}")
    return Decimal(match.group(0).replace(",", ""))


def _payment_amount_text(amount: Decimal) -> str:
    normalized = amount.quantize(Decimal("0.01"))
    if normalized == normalized.to_integral_value():
        return str(int(normalized))
    return f"{normalized:.2f}"


def _wait_for_remaining_balance(invoice_scope, expected_amount: str) -> None:
    expected = Decimal(expected_amount).quantize(Decimal("0.01"))
    deadline = time.monotonic() + 10000 / 1000
    while time.monotonic() < deadline:
        try:
            current = _invoice_total_amount(invoice_scope).quantize(Decimal("0.01"))
            if current == expected:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise AssertionError(f"Invoice balance did not update to {expected_amount}")


def _record_payment(page: Page, invoice_scope, dialog, amount: str) -> None:
    amount_input = _find_amount_input(dialog)
    _fill_payment_amount(dialog, amount_input, amount)
    _commit_payment_amount(dialog, amount_input)

    _select_cash_method(invoice_scope, dialog)

    _assert_recordable_amount(dialog, amount_input, amount)
    record_button = dialog.get_by_role("button", name="Record")
    record_button.wait_for(state="visible", timeout=5000)
    record_button.click(force=True)
    dialog.wait_for(state="hidden", timeout=5000)


def test_record_payment_multiple(page: Page, context: dict) -> None:
    """
    Record two payments for the same invoice.

    Prerequisites:
    - User is logged in (from category _setup)
    - Payment gateway is NOT connected

    Saves to context:
    - recorded_payment_first_amount
    - recorded_payment_second_amount
    """
    _create_invoice_for_payment(page, context)
    invoice_scope = _get_billing_scope(page)
    first_amount = "20"
    second_amount = _payment_amount_text(_invoice_total_amount(invoice_scope) - Decimal(first_amount))

    dialog = _open_record_payment_dialog(page, invoice_scope)
    _record_payment(page, invoice_scope, dialog, first_amount)

    invoice_scope = _get_billing_scope(page)
    _wait_for_remaining_balance(invoice_scope, second_amount)
    dialog = _open_record_payment_dialog(page, invoice_scope)
    _record_payment(page, invoice_scope, dialog, second_amount)

    context["recorded_payment_first_amount"] = first_amount
    context["recorded_payment_second_amount"] = second_amount

