"""Shared UI helpers for the partial-refund subcategories.

Navigation, partial-refund dialog interaction, and payment-page assertions.
Reused by both the POS and back-office partial-refund tests.
"""

import re
import time

from playwright.sync_api import Page, expect

FAST_UI_TIMEOUT = 5000
STATE_TIMEOUT = 15000
REFUND_COMPLETION_TIMEOUT = 30000


def get_billing_scope(page: Page):
    """Angular billing content renders inside the angularjs iframe."""
    if page.locator(".payment-component, .summary-header").count() > 0:
        return page
    iframe = page.locator('iframe[title="angularjs"]')
    if iframe.count() > 0:
        iframe.first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
        return page.frame_locator('iframe[title="angularjs"]')
    return page


def first_visible(locators, timeout: int = FAST_UI_TIMEOUT):
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


def page_text(page: Page) -> str:
    parts = [page.evaluate("() => document.body.innerText")]
    for frame in page.frames:
        try:
            parts.append(frame.evaluate("() => document.body.innerText"))
        except Exception:
            continue
    return "\n".join(parts)


def open_payments_received(page: Page):
    if "/app/payments/transactions" not in page.url:
        payments_link = page.get_by_text("Payments Received", exact=True)
        if payments_link.count() > 0 and payments_link.first.is_visible():
            payments_link.first.click(timeout=FAST_UI_TIMEOUT)
        else:
            sales = page.locator('[data-qa="nav-sales"]')
            if sales.count() == 0:
                sales = page.get_by_role("button", name="Sales").first
            else:
                sales = sales.first
            sales.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
            sales.click()
            payments_link = page.get_by_text("Payments Received", exact=True)
            payments_link.first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
            payments_link.first.click(timeout=FAST_UI_TIMEOUT)
        page.wait_for_url(
            "**/app/payments/transactions**",
            wait_until="domcontentloaded",
            timeout=STATE_TIMEOUT,
        )
    return get_billing_scope(page)


def open_payment_by_name(page: Page, client_name: str, payment_name: str):
    """Open the payment whose title matches payment_name from Payments Received."""
    scope = open_payments_received(page)
    search = scope.locator('input[name="name_filter"]').first
    search.wait_for(state="visible", timeout=STATE_TIMEOUT)
    search.fill(client_name, timeout=FAST_UI_TIMEOUT)

    link = scope.locator("a").filter(has_text=payment_name).first
    deadline = time.monotonic() + STATE_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if link.count() > 0 and link.is_visible():
            break
        time.sleep(0.3)
    link.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    link.evaluate("(element) => element.click()")
    page.wait_for_url(
        "**/app/payments/transactions/**",
        wait_until="domcontentloaded",
        timeout=STATE_TIMEOUT,
    )
    return get_billing_scope(page)


def _trigger_refund_action(page: Page, scope) -> None:
    refund = first_visible(
        [scope.locator('[data-qa="refund"]'), page.locator('[data-qa="refund"]')],
        timeout=1000,
    )
    if refund is None:
        more = first_visible(
            [scope.locator('[data-qa="ps-more-actions"]'), page.locator('[data-qa="ps-more-actions"]')],
            timeout=FAST_UI_TIMEOUT,
        )
        if more is None:
            raise AssertionError("Neither refund nor more-actions control was visible")
        more.click(force=True, timeout=FAST_UI_TIMEOUT)
        refund = first_visible(
            [scope.locator('[data-qa="refund"]'), page.locator('[data-qa="refund"]')],
            timeout=FAST_UI_TIMEOUT,
        )
        if refund is None:
            raise AssertionError("Refund action did not appear after opening more-actions")
    refund.evaluate("(element) => element.click()")


def _refund_amount_input(page: Page, timeout: int = STATE_TIMEOUT):
    """Find the refund-amount input across all frames (the dialog may nest in vuetage)."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            found = first_visible(
                [
                    frame.locator('.refund-details-container__amount-container [data-qa="VcCounter"] input'),
                    frame.locator('[data-qa="VcCounter"] input'),
                    frame.get_by_label("Refund amount"),
                ],
                timeout=300,
            )
            if found is not None:
                return found
        time.sleep(0.2)
    return None


def _refund_submit_button(page: Page, timeout: int = STATE_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            found = first_visible(
                [
                    frame.locator('[data-qa="vc-footer-Mark as refunded"]'),
                    frame.locator('[data-qa="vc-footer-Refund"]'),
                    frame.get_by_role("button", name=re.compile(r"^(Mark as refunded|Refund)$", re.I)),
                ],
                timeout=300,
            )
            if found is not None:
                return found
        time.sleep(0.2)
    return None


def _set_refund_amount(amount_input, amount: str) -> None:
    expect(amount_input).to_be_enabled(timeout=FAST_UI_TIMEOUT)
    amount_input.fill(amount, timeout=FAST_UI_TIMEOUT)
    amount_input.press("Tab", timeout=FAST_UI_TIMEOUT)
    if amount not in (amount_input.input_value(timeout=FAST_UI_TIMEOUT) or ""):
        amount_input.click(timeout=FAST_UI_TIMEOUT)
        amount_input.press("ControlOrMeta+A", timeout=FAST_UI_TIMEOUT)
        amount_input.press("Backspace", timeout=FAST_UI_TIMEOUT)
        amount_input.press_sequentially(amount, delay=50)
        amount_input.press("Tab", timeout=FAST_UI_TIMEOUT)


def _wait_for_refund_completion(page: Page) -> None:
    deadline = time.monotonic() + REFUND_COMPLETION_TIMEOUT / 1000
    while time.monotonic() < deadline:
        text = page_text(page).lower()
        if "refund" in text and ("-$" in page_text(page) or "marked as refunded" in text):
            return
        time.sleep(0.5)


def partial_refund_current_payment(page: Page, amount: str) -> None:
    """On an open payment page, issue a partial refund of `amount`."""
    scope = get_billing_scope(page)
    _trigger_refund_action(page, scope)

    amount_input = _refund_amount_input(page)
    if amount_input is None:
        raise AssertionError("Refund amount input did not appear")
    _set_refund_amount(amount_input, amount)

    submit = _refund_submit_button(page)
    if submit is None:
        raise AssertionError("Refund confirm button did not appear")
    expect(submit).to_be_enabled(timeout=STATE_TIMEOUT)
    submit.click(timeout=FAST_UI_TIMEOUT)
    _wait_for_refund_completion(page)


def assert_payment_page(page: Page, name: str, amount: str, refund_amount: str) -> None:
    """Verify the payment page shows the expected name, amount, and refund amount."""
    scope = get_billing_scope(page)
    header = scope.locator("div.summary-header h3").first
    header.wait_for(state="visible", timeout=STATE_TIMEOUT)

    deadline = time.monotonic() + STATE_TIMEOUT / 1000
    actual_name = actual_amount = actual_refund = ""
    while time.monotonic() < deadline:
        actual_name = (header.text_content() or "").strip()
        actual_amount = (scope.locator("div.summary-header h2 span").first.text_content() or "").strip()
        refund_loc = scope.locator(".refund-amount").first
        actual_refund = (refund_loc.text_content() or "").strip() if refund_loc.count() > 0 else ""
        if name in actual_name and amount in actual_amount and refund_amount in actual_refund:
            return
        time.sleep(0.5)

    if name not in actual_name:
        raise AssertionError(f"Expected payment name '{name}', got '{actual_name}'")
    if amount not in actual_amount:
        raise AssertionError(f"Expected amount '{amount}', got '{actual_amount}'")
    if refund_amount not in actual_refund:
        raise AssertionError(f"Expected refund amount '{refund_amount}', got '{actual_refund}'")
