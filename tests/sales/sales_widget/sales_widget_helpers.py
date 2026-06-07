"""Helpers for the Sales Widget scenarios (migrated from automation-js).

Covers the new-dashboard Sales widget: API seeding of the revenue / pending
estimate / overdue-appointment data, locating the widget (POV top document or an
embedded frame), the empty-state + payment-wizard assertions, reading the
aggregated widget values, and the click-through navigation to the back-office
payments / estimates / billing pages.

Selector policy (prefer-data-qa-selectors): the widget exposes data-qa
attributes for every value (`PaymentWidget-TotalRevenue|PendingEstimates|
OverduePayments`) and for the empty-state button, and the back-office page headers
are addressed by their POV `data-qa` header ids; those are reused directly. The
loaded-widget container (`.sales-widget--loaded`), the empty-state title, and the
payment-wizard root have no data-qa, so the stable legacy CSS is reused (matching
pages/desktop/Frontage/Payments/salesWidget.js); those data-qa should be added in
the product code.

Waits: element/interaction waits are capped at 5s (STATE_TIMEOUT). NAV_TIMEOUT is
the dashboard/iframe render-readiness budget. The aggregated values (revenue and
overdue buckets) are computed by a backend rollup that lags the API writes, so
``assert_widget_values`` reloads the dashboard and polls up to AGG_TIMEOUT — a
bounded eventual-consistency budget, not a fixed sleep.
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timedelta, timezone

from playwright.sync_api import Page

from tests.account_api import (
    account_request,
    create_service_via_api,
    enable_features,
    first_staff_uid,
    pivot_uid,
)

NEW_DASHBOARD_FLAG = "new_dashboard"

STATE_TIMEOUT = 5000
# NAV_TIMEOUT is the dashboard/iframe render-readiness budget (POV dashboard boot +
# embedded widget frame); a documented bounded exception to the 5s element cap,
# halved from the original 20s.
NAV_TIMEOUT = 10000
AGG_TIMEOUT = 40  # seconds; bounded eventual-consistency poll for the rollup

WIDGET_CONTAINER = ".sales-widget.sales-widget--loaded"
EMPTY_TITLE = ".payment-widget-list__empty-state-title"
EMPTY_LIST = "[data-qa='PaymentWidgetListEmptyState']"
EMPTY_BUTTON = "[data-qa='PaymentWidgetListEmptyState'] .VcEmptyStateButton"
PAYMENT_WIZARD = ".wizard-content.payment-wizard-get-paid-online"

TOTAL_REVENUE = "[data-qa='PaymentWidget-TotalRevenue'] .widget-data__value"
PENDING_ESTIMATES = "[data-qa='PaymentWidget-PendingEstimates'] .widget-data__value"
OVERDUE_PAYMENTS = "[data-qa='PaymentWidget-OverduePayments'] .widget-data__value"
OVERDUE_BREAKDOWN = (
    "[data-qa='PaymentWidget-OverduePayments'] .overdue-breakdown-list .overdue-breakdown"
)

REDIRECT_TITLES = {
    "payments": "Payments Received",
    "estimates": "Estimates",
    "billing": "Billing & Invoicing",
}

# Back-office destination page headers, addressed by their POV data-qa ids (matches
# legacy paymentsReceived/estimatesList/billingAndInvoicing page objects).
REDIRECT_HEADERS = {
    "payments": '[data-qa="Payments Received"]',
    "estimates": "[data-qa='Estimates']",
    "billing": '[data-qa="Billing & Invoicing"]',
}


# --------------------------------------------------------------------------- #
# API setup
# --------------------------------------------------------------------------- #
def enable_new_dashboard(context: dict) -> None:
    """Enable the new_dashboard flag so the dashboard renders the Sales widget."""
    enable_features(context, NEW_DASHBOARD_FLAG)


def create_fee_service(context: dict, name: str, price: int | str) -> dict:
    """Create a 'display a fee' appointment service (charge_type paid_non_secured)."""
    return create_service_via_api(
        context, name, charge_type="paid_non_secured", price=str(price)
    )


def schedule_past_appointment(context: dict, service: dict, client: dict, days_ago: int) -> dict:
    """Book an appointment `days_ago` days in the past so its fee becomes overdue."""
    start = (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(
        minute=0, second=0, microsecond=0
    )
    response = account_request(
        context,
        "POST",
        "/business/scheduling/v1/bookings",
        json={
            "business_id": pivot_uid(context),
            "staff_id": first_staff_uid(context),
            "start_time": start.isoformat().replace("+00:00", "Z"),
            "service_id": service["id"],
            "client_id": client["id"],
        },
    )
    data = response.get("data") or response
    return data.get("booking") or data


def create_invoice(context: dict, title: str, client: dict, items: list[dict]) -> dict:
    """Create an invoice due next month (POST /platform/v1/invoices)."""
    due_date = (datetime.now(timezone.utc) + timedelta(days=30)).date().isoformat()
    payload = {
        "title": title,
        "client_id": client["id"],
        "address": "tlv",
        "currency": "USD",
        "due_date": due_date,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
        "send_email": False,
    }
    response = account_request(context, "POST", "/platform/v1/invoices", json=payload)
    data = response.get("data") or response
    invoice = data.get("invoice") or data
    invoice["id"] = invoice.get("id") or invoice.get("uid")
    if not invoice["id"]:
        raise ValueError(f"Invoice API response did not include an id: {response}")
    return invoice


def record_payment(
    context: dict,
    title: str,
    client_id: str,
    amount: str | int,
    subject_id: str,
    subject_type: str,
    *,
    method: str = "Cash",
) -> dict:
    """Record a payment (POST /platform/v1/payments) so it counts toward revenue."""
    payload = {
        "title": title,
        "client_id": client_id,
        "amount": amount,
        "currency": "USD",
        "payment_method": method,
        "payment_subject_id": subject_id,
        "payment_subject_type": subject_type,
    }
    response = account_request(context, "POST", "/platform/v1/payments", json=payload)
    data = response.get("data") or response
    return data.get("payment") or data


# --------------------------------------------------------------------------- #
# UI navigation + widget scope
# --------------------------------------------------------------------------- #
def _app_base(context: dict) -> str:
    return (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")


def goto_new_dashboard(page: Page, context: dict) -> None:
    page.goto(f"{_app_base(context)}/app/dashboard", wait_until="domcontentloaded")


def _widget_scope(page: Page):
    """Return the page or embedded frame that contains the loaded Sales widget."""
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        try:
            if page.locator(WIDGET_CONTAINER).count() > 0:
                return page
        except Exception:
            pass
        for frame in page.frames:
            try:
                if frame.locator(WIDGET_CONTAINER).count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError("Sales widget (.sales-widget--loaded) not found on the dashboard")


# --------------------------------------------------------------------------- #
# Empty state + wizard
# --------------------------------------------------------------------------- #
def assert_empty_state(page: Page):
    """Assert the Sales widget shows its empty state (title, list, CTA button)."""
    scope = _widget_scope(page)
    for selector in (EMPTY_TITLE, EMPTY_LIST, EMPTY_BUTTON):
        scope.locator(selector).first.wait_for(state="visible", timeout=STATE_TIMEOUT)
    return scope


def open_payment_wizard(page: Page) -> None:
    """Click "Start accepting payments" and assert the payment wizard opens."""
    scope = _widget_scope(page)
    scope.locator(EMPTY_BUTTON).first.click(timeout=STATE_TIMEOUT)
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        try:
            if page.locator(PAYMENT_WIZARD).count() > 0:
                page.locator(PAYMENT_WIZARD).first.wait_for(state="visible", timeout=STATE_TIMEOUT)
                return
        except Exception:
            pass
        for frame in page.frames:
            try:
                if frame.locator(PAYMENT_WIZARD).count() > 0:
                    frame.locator(PAYMENT_WIZARD).first.wait_for(
                        state="visible", timeout=STATE_TIMEOUT
                    )
                    return
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError("Payment wizard (payment-wizard-get-paid-online) did not open")


# --------------------------------------------------------------------------- #
# Values
# --------------------------------------------------------------------------- #
def read_widget_values(page: Page) -> dict:
    scope = _widget_scope(page)

    def value(selector: str) -> str:
        locator = scope.locator(selector).first
        locator.wait_for(state="visible", timeout=STATE_TIMEOUT)
        return (locator.inner_text() or "").strip()

    breakdowns = []
    rows = scope.locator(OVERDUE_BREAKDOWN)
    for index in range(rows.count()):
        text = (rows.nth(index).inner_text() or "").strip()
        breakdowns.append(re.sub(r"\s*\|\s*", ",", text))

    return {
        "total_revenue": value(TOTAL_REVENUE),
        "pending_estimates": value(PENDING_ESTIMATES),
        "overdue_payments": value(OVERDUE_PAYMENTS),
        "breakdowns": breakdowns,
    }


def assert_widget_values(page: Page, context: dict, expected: dict) -> None:
    """Reload the dashboard and poll until the widget matches `expected`.

    The revenue total and overdue age buckets are produced by a backend rollup
    that lags the API writes, so this reloads and re-reads up to AGG_TIMEOUT
    (bounded eventual-consistency budget) instead of a single fixed wait."""
    deadline = time.monotonic() + AGG_TIMEOUT
    last: dict = {}
    while time.monotonic() < deadline:
        goto_new_dashboard(page, context)
        try:
            last = read_widget_values(page)
        except AssertionError:
            page.wait_for_timeout(2000)
            continue
        if all(last.get(key) == expected[key] for key in expected):
            return
        page.wait_for_timeout(2000)
    raise AssertionError(f"Sales widget values mismatch.\n  expected={expected}\n  got     ={last}")


def assert_redirect(page: Page, context: dict, value_selector: str, target: str) -> None:
    """Click a widget value and assert the matching back-office page header shows.

    Mirrors legacy redirect verification (getPaymentsReceivedHeader /
    getEstimatesPageHeader / getBillingAndInvoicingHeader), which assert the POV
    page-header `data-qa` id (`[data-qa="Payments Received"]` etc.)."""
    goto_new_dashboard(page, context)
    scope = _widget_scope(page)
    scope.locator(value_selector).first.click(timeout=STATE_TIMEOUT)

    header = REDIRECT_HEADERS[target]
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        for frame in [page, *page.frames]:
            try:
                loc = frame.locator(header).first
                if loc.count() > 0 and loc.is_visible():
                    return
            except Exception:
                continue
        page.wait_for_timeout(300)
    raise AssertionError(f"Redirect to '{REDIRECT_TITLES[target]}' "
                         f"page header ({header}) was not visible after click")
