import re
import sys
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import requests
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

FAST_UI_TIMEOUT = 5000
MENU_TIMEOUT = 1000
STATE_TIMEOUT = 15000
REFUND_COMPLETION_TIMEOUT = 30000
REQUEST_TIMEOUT = 30


def _get_billing_scope(page: Page):
    if page.locator(".payment-component").count() > 0:
        return page
    iframe = page.locator('iframe[title="angularjs"]')
    if iframe.count() > 0:
        iframe.first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
        return page.frame_locator('iframe[title="angularjs"]')
    return page


def _wait_for_invoice_component(page: Page, timeout: int = FAST_UI_TIMEOUT):
    invoice_scope = _get_billing_scope(page)
    invoice_scope.locator(".payment-component").first.wait_for(state="visible", timeout=timeout)
    return invoice_scope


def _first_visible(locators, timeout: int = FAST_UI_TIMEOUT):
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


def _open_billing(page: Page):
    if "/app/payments/orders" not in page.url:
        billing_link = page.get_by_text("Billing & Invoicing", exact=True)
        if billing_link.count() > 0 and billing_link.first.is_visible():
            billing_link.first.click()
        else:
            sales = page.locator('[data-qa="nav-sales"]')
            if sales.count() == 0:
                sales = page.get_by_role("button", name="Sales").first
            sales.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
            sales.click()
            billing_link = page.get_by_text("Billing & Invoicing", exact=True)
            billing_link.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
            billing_link.click()
        page.wait_for_url("**/app/payments/orders", timeout=FAST_UI_TIMEOUT)
    return _get_billing_scope(page)


def _include_not_yet_due_filter(page: Page, billing_scope) -> None:
    try:
        clear_selection = billing_scope.get_by_text("CLEAR SELECTION", exact=True).first
        if clear_selection.count() > 0 and clear_selection.is_visible():
            clear_selection.click(timeout=FAST_UI_TIMEOUT)
            page.keyboard.press("Escape")

        status_filter = billing_scope.locator('[name="status_filter"]').first
        if status_filter.count() == 0 or not status_filter.is_visible():
            return
        status_filter.click(force=True)
        for value in ("issued", "due", "not_yet_due", "paid", "credited", "partially_credited"):
            status = billing_scope.locator(f'[value="{value}"]').first
            if status.count() == 0 or not status.is_visible():
                continue
            checked = status.evaluate(
                """element => element.checked === true || element.getAttribute('aria-checked') === 'true'"""
            )
            if not checked:
                status.click(force=True)
        page.keyboard.press("Escape")
        page.keyboard.press("Escape")
    except Exception:
        pass


def _page_text(page: Page) -> str:
    parts = [page.evaluate("() => document.body.innerText")]
    for frame in page.frames:
        try:
            parts.append(frame.evaluate("() => document.body.innerText"))
        except Exception:
            continue
    return "\n".join(parts)


def _wait_for_page_text(page: Page, text: str, timeout: int = STATE_TIMEOUT) -> str:
    deadline = time.monotonic() + timeout / 1000
    last_text = ""
    while time.monotonic() < deadline:
        last_text = _page_text(page)
        if text in last_text:
            return last_text
        time.sleep(0.5)
    return last_text


def _account_request(context: dict, method: str, path: str, **kwargs) -> dict:
    auto_account = context.get("auto_account") or {}
    token = auto_account.get("api_token") or auto_account.get("auth_token")
    if not token:
        raise ValueError("auto_account api_token is missing from context")
    response = requests.request(
        method,
        f"{context['api_base_url'].rstrip('/')}{path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=REQUEST_TIMEOUT,
        **kwargs,
    )
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason} for {path}: {response.text[:500]}",
            response=response,
        )
    return response.json()


def _create_invoice(page: Page, context: dict, base_title: str, starting_number: int) -> dict:
    now = datetime.now(timezone.utc)
    response = _account_request(
        context,
        "POST",
        "/platform/v1/invoices",
        json={
            "title": base_title,
            "client_id": context["created_client_id"],
            "address": "Rome, Italy",
            "currency": "USD",
            "due_date": (now + timedelta(days=30)).isoformat(),
            "issued_at": now.isoformat(),
            "items": [
                {
                    "title": context["invoice_service_name"],
                    "amount": context.get("invoice_service_price", "100"),
                    "quantity": 1,
                }
            ],
            "send_email": False,
            "allow_online_payment": False,
        },
    )
    payload = response.get("data") or response
    created = payload.get("invoice") or payload
    title = created.get("title") or base_title
    invoice = {
        "id": created.get("id") or created.get("uid"),
        "title": title,
        "number": str(created.get("number") or starting_number),
        "amount": "$100.00",
        "payment_status_uid": created.get("payment_status_uid")
        or (created.get("payment_status") or {}).get("uid")
        or created.get("payment_status_id"),
    }
    context.setdefault("eu_strict_invoice_ids", {})[title] = invoice["id"]
    if invoice["payment_status_uid"]:
        context.setdefault("eu_strict_payment_status_uids", {})[title] = invoice["payment_status_uid"]
    _open_invoice_by_title(page, title, context)
    return invoice


def _open_invoice_by_title(page: Page, title: str, context: dict | None = None):
    if "/app/invoices/" in page.url:
        try:
            invoice_scope = _wait_for_invoice_component(page)
            body_text = _page_text(page)
            if title in body_text:
                return invoice_scope
        except PlaywrightTimeoutError:
            pass

    if "/app/payments/transactions/" in page.url:
        scope = _get_billing_scope(page)
        view_invoice = _first_visible(
            [
                scope.get_by_role("button", name=re.compile(r"^View Invoice$", re.I)),
                scope.get_by_text("View Invoice", exact=True),
                scope.locator('[data-qa="view_invoice"]'),
            ],
            timeout=FAST_UI_TIMEOUT,
        )
        if view_invoice is not None:
            try:
                view_invoice.evaluate("(element) => element.click()")
                page.wait_for_url(
                    "**/app/invoices/**",
                    wait_until="domcontentloaded",
                    timeout=FAST_UI_TIMEOUT,
                )
                invoice_scope = _wait_for_invoice_component(page)
                _wait_for_page_text(page, title, timeout=FAST_UI_TIMEOUT)
                return invoice_scope
            except PlaywrightTimeoutError:
                pass

    billing_scope = _open_billing(page)
    _include_not_yet_due_filter(page, billing_scope)
    link = billing_scope.locator("a").filter(has_text=title).first
    if link.count() == 0 or not link.is_visible():
        try:
            link.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
        except Exception:
            pass
    if link.count() > 0 and link.is_visible():
        _open_invoice_link(page, link, title)
        return _get_billing_scope(page)

    search = billing_scope.locator('input[name="name_filter"]').first
    search.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    deadline = time.monotonic() + STATE_TIMEOUT / 1000
    link = billing_scope.locator("a").filter(has_text=title).first
    while time.monotonic() < deadline:
        search.fill(title, timeout=FAST_UI_TIMEOUT)
        if link.count() > 0 and link.is_visible():
            break
        time.sleep(0.5)
    link.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    _open_invoice_link(page, link, title)
    return _get_billing_scope(page)


def _open_invoice_link(page: Page, link, title: str) -> None:
    page.keyboard.press("Escape")
    link.evaluate("(element) => element.click()")
    try:
        page.wait_for_url(
            "**/app/invoices/**",
            wait_until="domcontentloaded",
            timeout=FAST_UI_TIMEOUT,
        )
    except PlaywrightTimeoutError:
        if "/app/invoices/" not in page.url:
            raise
    _wait_for_invoice_component(page)
    _wait_for_page_text(page, title, timeout=FAST_UI_TIMEOUT)


def _search_orders(page: Page, title: str, context: dict) -> None:
    _open_invoice_by_title(page, title, context)
    body_text = _wait_for_page_text(page, title)
    if title not in body_text:
        raise AssertionError(f"Expected invoice {title} to be accessible from orders")


def _assert_invoice(page: Page, title: str, state: str, amount: str, credit_status: str | None = None) -> None:
    deadline = time.monotonic() + STATE_TIMEOUT / 1000
    body_text = ""
    while time.monotonic() < deadline:
        body_text = _page_text(page)
        expected_values = [
            title in body_text,
            state.lower() in body_text.lower(),
            amount in body_text,
            "first last" in body_text,
            credit_status is None or credit_status.lower() in body_text.lower(),
        ]
        if all(expected_values):
            return
        time.sleep(0.5)

    if title not in body_text:
        raise AssertionError(f"Expected invoice {title} in invoice page")
    if state.lower() not in body_text.lower():
        raise AssertionError(f"Expected invoice state {state} in invoice page")
    if amount not in body_text:
        raise AssertionError(f"Expected invoice amount {amount} in invoice page")
    if "first last" not in body_text:
        raise AssertionError("Expected invoice client first last in invoice page")
    if credit_status and credit_status.lower() not in body_text.lower():
        raise AssertionError(f"Expected invoice credit status {credit_status} in invoice page")


def _open_record_payment_dialog(page: Page, invoice_scope):
    record = _first_visible(
        [
            page.locator('.take-payment-menu-content [data-qa="record"]'),
            invoice_scope.locator('.take-payment-menu-content [data-qa="record"]'),
        ],
        timeout=MENU_TIMEOUT,
    )
    if record is not None:
        record.click(force=True, timeout=FAST_UI_TIMEOUT)
        dialog = invoice_scope.locator("md-dialog").filter(
            has_text=re.compile("Record payment", re.I)
        ).first
        dialog.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
        return dialog

    for attempt in range(2):
        try:
            take_payment = invoice_scope.locator('[data-qa="take_payment"]').first
            if take_payment.count() == 0:
                take_payment = invoice_scope.get_by_role(
                    "button", name=re.compile(r"^Take payment", re.I)
                ).first
            take_payment.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
            take_payment.scroll_into_view_if_needed(timeout=FAST_UI_TIMEOUT)
            if attempt == 0:
                take_payment.click(force=True, timeout=FAST_UI_TIMEOUT)
            else:
                take_payment.evaluate("(element) => element.click()")

            record = _first_visible(
                [
                    page.locator('.take-payment-menu-content [data-qa="record"]'),
                    invoice_scope.locator('.take-payment-menu-content [data-qa="record"]'),
                ],
                timeout=MENU_TIMEOUT,
            )
            if record is not None:
                record.click(force=True, timeout=FAST_UI_TIMEOUT)
                dialog = invoice_scope.locator("md-dialog").filter(
                    has_text=re.compile("Record payment", re.I)
                ).first
                dialog.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
                return dialog
        except Exception:
            if _record_payment_dialog_is_visible(page):
                return None
            continue

    record = _first_visible(
        [
            page.get_by_role("menuitem", name=re.compile("Record payment", re.I)),
            invoice_scope.get_by_role("menuitem", name=re.compile("Record payment", re.I)),
            page.get_by_text("Record payment", exact=True),
            invoice_scope.get_by_text("Record payment", exact=True),
        ],
        timeout=MENU_TIMEOUT,
    )
    if record is not None:
        record.click(force=True, timeout=FAST_UI_TIMEOUT)
        dialog = invoice_scope.locator("md-dialog").filter(
            has_text=re.compile("Record payment", re.I)
        ).first
        dialog.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
        return dialog

    for frame in page.frames:
        try:
            opened = frame.evaluate(
                """() => {
                    const element = document.querySelector('.payment-component');
                    if (!element || !window.angular) return false;
                    const injector = window.angular.element(document.body).injector();
                    const rootScope = injector && injector.get('$rootScope');
                    if (!rootScope) return false;
                    rootScope.$broadcast('actions.invoice', null, 'record');
                    rootScope.$applyAsync && rootScope.$applyAsync();
                    return true;
                }"""
            )
            if opened:
                dialog = invoice_scope.locator("md-dialog").filter(
                    has_text=re.compile("Record payment", re.I)
                ).first
                try:
                    dialog.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
                    return dialog
                except Exception:
                    if _record_payment_dialog_is_visible(page):
                        return None
                    raise
        except Exception:
            continue

    raise AssertionError("Record payment action did not appear after opening Take payment")


def _record_payment_dialog_is_visible(page: Page) -> bool:
    for frame in page.frames:
        try:
            if frame.evaluate(
                """() => {
                    const visible = element => {
                        if (!element) return false;
                        const style = window.getComputedStyle(element);
                        const rect = element.getBoundingClientRect();
                        return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
                    };
                    return Array.from(document.querySelectorAll('md-dialog, [role="dialog"], .md-dialog-container'))
                        .some(element => visible(element) && element.innerText.includes('Record payment'));
                }"""
            ):
                return True
        except Exception:
            continue
    return False


def _submit_visible_record_payment_dialog(page: Page) -> bool:
    for frame in page.frames:
        try:
            submitted = frame.evaluate(
                """() => {
                    const visible = element => {
                        if (!element) return false;
                        const style = window.getComputedStyle(element);
                        const rect = element.getBoundingClientRect();
                        return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
                    };
                    const dialog = Array.from(document.querySelectorAll('md-dialog, [role="dialog"], .md-dialog-container'))
                        .find(element => visible(element) && element.innerText.includes('Record payment'));
                    if (!dialog) return false;
                    const scope = window.angular && window.angular.element(dialog).scope();
                    if (scope && scope.payment && typeof scope.recordPayment === 'function') {
                        scope.payment.payment_method = 'Cash';
                        scope.payment.send_receipt = false;
                        scope.recordPayment();
                        scope.$applyAsync && scope.$applyAsync();
                        return true;
                    }
                    const method = Array.from(dialog.querySelectorAll('[role="listbox"], md-select'))
                        .find(visible);
                    if (!method) return false;
                    method.click();
                    setTimeout(() => {
                        const cash = Array.from(document.querySelectorAll('md-option, [role="option"], button, div'))
                            .find(element => visible(element) && (element.innerText || '').trim() === 'Cash');
                        if (cash) cash.click();
                        const record = Array.from(dialog.querySelectorAll('button, [role="button"]'))
                            .find(element => visible(element) && /^Record$/i.test((element.innerText || '').trim()));
                        if (record) record.click();
                    }, 250);
                    return true;
                }"""
            )
            if submitted:
                return True
        except Exception:
            continue
    return False


def _record_cash_payment(page: Page, context: dict, title: str) -> None:
    invoice_scope = _open_invoice_by_title(page, title, context)
    dialog = _open_record_payment_dialog(page, invoice_scope)
    if dialog is None:
        if not _submit_visible_record_payment_dialog(page):
            raise AssertionError("Record payment dialog did not submit")
        _wait_for_page_text(page, "PAID")
        return
    method = dialog.get_by_role("listbox", name="Payment received via")
    method.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    method.click(timeout=FAST_UI_TIMEOUT)
    cash_option = _first_visible(
        [
            page.get_by_role("option", name="Cash"),
            invoice_scope.get_by_role("option", name="Cash"),
        ],
        timeout=FAST_UI_TIMEOUT,
    )
    if cash_option is not None:
        cash_option.click(timeout=FAST_UI_TIMEOUT)
    record_button = dialog.get_by_role("button", name="Record")
    record_button.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    record_button.click(force=True, timeout=FAST_UI_TIMEOUT)
    dialog.wait_for(state="hidden", timeout=FAST_UI_TIMEOUT)


def _open_payments_received(page: Page):
    if "/app/payments/transactions" not in page.url:
        payments_link = page.get_by_text("Payments Received", exact=True)
        if payments_link.count() > 0 and payments_link.first.is_visible():
            payments_link.first.click(timeout=FAST_UI_TIMEOUT)
        else:
            sales = page.locator('[data-qa="nav-sales"]')
            if sales.count() == 0:
                sales = page.get_by_role("button", name="Sales").first
            sales.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
            sales.click()
            payments_link = page.get_by_text("Payments Received", exact=True)
            if payments_link.count() > 0:
                payments_link.first.click(timeout=FAST_UI_TIMEOUT)
            else:
                page.goto(
                    f"{page.url.split('/app/')[0]}/app/payments/transactions",
                    wait_until="domcontentloaded",
                    timeout=FAST_UI_TIMEOUT,
                )
        page.wait_for_url(
            "**/app/payments/transactions**",
            wait_until="domcontentloaded",
            timeout=FAST_UI_TIMEOUT,
        )
    return _get_billing_scope(page)


def _refund_payment(page: Page, context: dict, title: str, amount: str | None = None) -> None:
    scope = _open_payments_received(page)
    refund = scope.locator('[data-qa="refund"]').first
    if "/app/payments/transactions/" not in page.url or refund.count() == 0 or not refund.is_visible():
        search = scope.locator('input[name="name_filter"]').first
        search.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
        search.fill(context.get("created_client_name", "first last"))

        payment_link = scope.locator("a").filter(
            has_text=re.compile(context.get("invoice_service_name", ""), re.I)
        ).first
        if payment_link.count() == 0:
            payment_link = scope.locator("a").filter(has_text=re.compile("first last", re.I)).first
        payment_link.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
        payment_link.click(force=True, timeout=FAST_UI_TIMEOUT)
        page.wait_for_url(
            "**/app/payments/transactions/**",
            wait_until="domcontentloaded",
            timeout=FAST_UI_TIMEOUT,
        )
        scope = _get_billing_scope(page)
        refund = scope.locator('[data-qa="refund"]').first

    if refund.count() == 0 or not refund.is_visible():
        more = scope.locator('[data-qa="ps-more-actions"]').first
        more.click(force=True, timeout=FAST_UI_TIMEOUT)
        refund = scope.locator('[data-qa="refund"]').first
    refund.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    refund.click(force=True, timeout=FAST_UI_TIMEOUT)
    refund_dialog = _first_visible(
        [
            scope.get_by_role("dialog").filter(has_text=re.compile("Mark as refunded|Issue refund|Refund details", re.I)),
            scope.locator("md-dialog").filter(has_text=re.compile("Mark as refunded|Issue refund|Refund details", re.I)),
            page.get_by_role("dialog").filter(has_text=re.compile("Mark as refunded|Issue refund|Refund details", re.I)),
            page.locator("md-dialog").filter(has_text=re.compile("Mark as refunded|Issue refund|Refund details", re.I)),
        ],
        timeout=FAST_UI_TIMEOUT,
    )
    if refund_dialog is None:
        refund.evaluate("(element) => element.click()")
        refund_dialog = _first_visible(
            [
                scope.get_by_role("dialog").filter(has_text=re.compile("Mark as refunded|Issue refund|Refund details", re.I)),
                scope.locator("md-dialog").filter(has_text=re.compile("Mark as refunded|Issue refund|Refund details", re.I)),
                page.get_by_role("dialog").filter(has_text=re.compile("Mark as refunded|Issue refund|Refund details", re.I)),
                page.locator("md-dialog").filter(has_text=re.compile("Mark as refunded|Issue refund|Refund details", re.I)),
            ],
            timeout=FAST_UI_TIMEOUT,
        )
    if refund_dialog is None:
        if _submit_visible_refund_dialog(page, amount):
            _wait_for_refund_completion(page)
            _dismiss_refund_dialog(page)
            return
        page_text = _page_text(page).lower()
        if "mark as refunded" in page_text and _refund_completion_visible(page):
            _dismiss_refund_dialog(page)
            return
        raise AssertionError("Refund dialog did not appear")

    if amount is not None:
        amount_input = _first_visible(
            [
                refund_dialog.locator('.refund-details-container__amount-container [data-qa="VcCounter"] input'),
                refund_dialog.get_by_label("Refund amount"),
            ],
            timeout=FAST_UI_TIMEOUT,
        )
        if amount_input is None:
            raise AssertionError("Refund amount input did not appear")
        expect(amount_input).to_be_enabled(timeout=FAST_UI_TIMEOUT)
        amount_input.fill(amount, timeout=FAST_UI_TIMEOUT)
        amount_input.press("Tab", timeout=FAST_UI_TIMEOUT)
        if amount not in amount_input.input_value(timeout=FAST_UI_TIMEOUT):
            amount_input.click(timeout=FAST_UI_TIMEOUT)
            amount_input.press("Meta+A" if sys.platform == "darwin" else "Control+A", timeout=FAST_UI_TIMEOUT)
            amount_input.press("Backspace", timeout=FAST_UI_TIMEOUT)
            amount_input.press_sequentially(amount, delay=50)
            amount_input.press("Tab", timeout=FAST_UI_TIMEOUT)
        if amount not in amount_input.input_value(timeout=FAST_UI_TIMEOUT):
            raise AssertionError(f"Refund amount was not set to {amount}: {amount_input.input_value(timeout=FAST_UI_TIMEOUT)}")

    footer = _first_visible(
        [
            refund_dialog.get_by_role("button", name=re.compile(r"^Mark as refunded$", re.I)),
            refund_dialog.locator('[data-qa="vc-footer-Mark as refunded"]'),
            refund_dialog.locator("button").filter(has_text=re.compile(r"^Mark as refunded$", re.I)),
        ],
        timeout=FAST_UI_TIMEOUT,
    )
    if footer is None:
        raise AssertionError("Mark as refunded action did not appear")
    expect(footer).to_be_enabled(timeout=FAST_UI_TIMEOUT)
    footer.click(force=True, timeout=FAST_UI_TIMEOUT)
    try:
        refund_dialog.wait_for(state="hidden", timeout=FAST_UI_TIMEOUT)
    except Exception:
        _wait_for_refund_completion(page)
        _dismiss_refund_dialog(page)


def _submit_visible_refund_dialog(page: Page, amount: str | None = None) -> bool:
    for frame in page.frames:
        try:
            submitted = frame.evaluate(
                """(amount) => {
                    const visible = element => {
                        if (!element) return false;
                        const style = window.getComputedStyle(element);
                        const rect = element.getBoundingClientRect();
                        return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
                    };
                    const dialog = Array.from(document.querySelectorAll('md-dialog, [role="dialog"], .md-dialog-container'))
                        .find(element => visible(element) && /Mark as refunded|Issue refund|Refund details/i.test(element.innerText || ''));
                    const container = dialog || document.body;
                    if (!/Mark as refunded|Issue refund|Refund details/i.test(container.innerText || '')) return false;
                    if (amount !== null) {
                        const refundArea = Array.from(container.querySelectorAll('[class*="refund"], [class*="Refund"]'))
                            .find(element => visible(element) && /Refund amount|Refund details/i.test(element.innerText || '')) || container;
                        const input = Array.from(refundArea.querySelectorAll('input'))
                            .find(element => visible(element) && /refund amount/i.test(element.getAttribute('aria-label') || element.placeholder || ''));
                        const fallbackInput = input || Array.from(refundArea.querySelectorAll('input'))
                            .find(element => visible(element) && !element.disabled);
                        if (!fallbackInput || fallbackInput.disabled) return false;
                        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        setter.call(fallbackInput, amount);
                        fallbackInput.dispatchEvent(new Event('input', { bubbles: true }));
                        fallbackInput.dispatchEvent(new Event('change', { bubbles: true }));
                        fallbackInput.dispatchEvent(new Event('blur', { bubbles: true }));
                    }
                    const submit = Array.from(container.querySelectorAll('button, [role="button"]'))
                        .find(element => visible(element)
                            && /^Mark as refunded$/i.test((element.innerText || '').trim())
                            && !element.disabled
                            && element.getAttribute('aria-disabled') !== 'true');
                    if (!submit) return false;
                    submit.click();
                    return true;
                }""",
                amount,
            )
            if submitted:
                return True
        except Exception:
            continue
    return False


def _refund_completion_visible(page: Page) -> bool:
    text = _page_text(page).lower()
    return (
        "credit note issued" in text
        or "credit note and refund issued" in text
        or "payment marked as refunded" in text
    )


def _wait_for_refund_completion(page: Page) -> None:
    deadline = time.monotonic() + REFUND_COMPLETION_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _refund_completion_visible(page):
            return
        time.sleep(0.5)
    raise AssertionError("Refund completion state did not appear")


def _dismiss_refund_dialog(page: Page) -> None:
    if "mark as refunded" not in _page_text(page).lower():
        return
    page.keyboard.press("Escape")
    time.sleep(0.2)
    if "mark as refunded" not in _page_text(page).lower():
        return

    for frame in page.frames:
        try:
            closed = frame.evaluate(
                """() => {
                    const visible = element => {
                        if (!element) return false;
                        const style = window.getComputedStyle(element);
                        const rect = element.getBoundingClientRect();
                        return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
                    };
                    const closeButton = Array.from(document.querySelectorAll('button, [role="button"], [aria-label]'))
                        .find(element => visible(element)
                            && (/close/i.test(element.getAttribute('aria-label') || '')
                                || ['×', 'x'].includes((element.innerText || '').trim().toLowerCase())));
                    if (!closeButton) return false;
                    closeButton.click();
                    return true;
                }"""
            )
            if closed:
                return
        except Exception:
            continue


def _credit_notes(invoice_scope) -> list[dict]:
    component = invoice_scope.locator(".payment-component").first
    component.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    return component.evaluate(
        """element => {
            const scope = window.angular && window.angular.element(element).scope();
            const invoice = scope && scope.InvoiceViewModel && scope.InvoiceViewModel.invoice;
            return (invoice && invoice.metadata && invoice.metadata.credit_notes) || [];
        }"""
    )


def _assert_credit_notes(invoice_scope, expected_count: int, expected_amounts: list[str] | None = None) -> None:
    deadline = time.monotonic() + STATE_TIMEOUT / 1000
    notes = []
    while time.monotonic() < deadline:
        notes = _credit_notes(invoice_scope)
        if len(notes) == expected_count:
            break
        time.sleep(0.5)
    if len(notes) != expected_count:
        raise AssertionError(f"Expected {expected_count} credit notes, found {len(notes)}")

    action = _visible_credit_notes_action(invoice_scope)
    expect(action).to_be_visible(timeout=FAST_UI_TIMEOUT)

    if expected_amounts:
        actual = [Decimal(str(note.get("amount", "0"))) for note in notes]
        expected = [Decimal(amount.replace("$", "")) for amount in expected_amounts]
        if actual[: len(expected)] != expected:
            raise AssertionError(f"Credit note amounts mismatch. Expected {expected}, got {actual}")


def _visible_credit_notes_action(invoice_scope):
    action = _first_visible(
        [
            invoice_scope.locator('f-entity-actions [data-qa="view_credit_notes"]').filter(
                has_text=re.compile(r"^VIEW CREDIT NOTES$", re.I)
            ),
            invoice_scope.locator('.actions [data-qa="view_credit_notes"]').filter(
                has_text=re.compile(r"^VIEW CREDIT NOTES$", re.I)
            ),
            invoice_scope.get_by_role("button", name=re.compile(r"^VIEW CREDIT NOTES$", re.I)),
            invoice_scope.locator('[data-qa="view_credit_notes"]'),
        ]
    )
    if action is not None:
        return action

    more = invoice_scope.locator('[data-qa="ps-more-actions"]').first
    more.click(force=True, timeout=FAST_UI_TIMEOUT)
    action = _first_visible(
        [
            invoice_scope.locator('[data-qa="view_credit_notes"]'),
            invoice_scope.get_by_text("View credit notes", exact=True),
        ]
    )
    if action is None:
        raise AssertionError("View credit notes action was not visible")
    return action


def _assert_credit_note_pdf_opens(page: Page, invoice_scope) -> None:
    action = _visible_credit_notes_action(invoice_scope)
    pages_before = len(page.context.pages)
    try:
        with page.context.expect_page(timeout=FAST_UI_TIMEOUT) as popup_info:
            action.click(force=True, timeout=FAST_UI_TIMEOUT)
        pdf_page = popup_info.value
    except PlaywrightTimeoutError as error:
        raise AssertionError("Credit note PDF tab did not open") from error

    try:
        if len(page.context.pages) <= pages_before:
            raise AssertionError("Credit note PDF tab did not open")
    finally:
        pdf_page.close()


def test_refund_credit_notes(page: Page, context: dict) -> None:
    page.set_default_timeout(FAST_UI_TIMEOUT)
    page.set_default_navigation_timeout(FAST_UI_TIMEOUT)
    start_number = int(str(int(time.time()))[-7:])

    print("  Step 1: Create first strict invoice via API")
    first_invoice = _create_invoice(page, context, "strict_invoice", start_number)
    print("  Step 2: Assert first invoice is issued")
    _assert_invoice(page, first_invoice["title"], "ISSUED", "$100.00")
    print("  Step 3: Search first invoice orders")
    _search_orders(page, first_invoice["title"], context)
    print("  Step 4: Record first invoice payment")
    _record_cash_payment(page, context, first_invoice["title"])
    print("  Step 5: Assert first invoice is paid")
    _assert_invoice(page, first_invoice["title"], "PAID", "$100.00")
    print("  Step 6: Refund first invoice")
    _refund_payment(page, context, first_invoice["title"])
    first_scope = _open_invoice_by_title(page, first_invoice["title"], context)
    print("  Step 7: Assert first invoice credit note")
    _assert_invoice(page, first_invoice["title"], "PAID", "$0.00", "CREDITED")
    print("    Invoice credited state verified")
    page.reload(wait_until="domcontentloaded", timeout=FAST_UI_TIMEOUT)
    _wait_for_page_text(page, first_invoice["title"], timeout=FAST_UI_TIMEOUT)
    first_scope = _get_billing_scope(page)
    _assert_credit_notes(first_scope, 1)
    _assert_credit_note_pdf_opens(page, first_scope)

    print("  Step 8: Create second strict invoice via API")
    second_invoice = _create_invoice(page, context, "strict_inv_2", start_number + 1)
    _assert_invoice(page, second_invoice["title"], "ISSUED", "$100.00")
    _record_cash_payment(page, context, second_invoice["title"])
    _assert_invoice(page, second_invoice["title"], "PAID", "$100.00")
    _refund_payment(page, context, second_invoice["title"], "60")
    _refund_payment(page, context, second_invoice["title"], "40")
    second_scope = _open_invoice_by_title(page, second_invoice["title"], context)
    _assert_invoice(page, second_invoice["title"], "PAID", "$0.00", "CREDITED")
    page.reload(wait_until="domcontentloaded", timeout=FAST_UI_TIMEOUT)
    _wait_for_page_text(page, second_invoice["title"], timeout=FAST_UI_TIMEOUT)
    second_scope = _get_billing_scope(page)
    _assert_credit_notes(second_scope, 2, ["$60.00", "$40.00"])

    context["eu_strict_first_invoice"] = first_invoice
    context["eu_strict_second_invoice"] = second_invoice
