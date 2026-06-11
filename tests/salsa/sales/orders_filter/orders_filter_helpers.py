"""Helpers for the Orders Filter scenario (migrated from automation-js).

Covers the back-office Orders (Billing & Invoicing) page: applying the payable
*type* filter (bookings / invoices / packages / products) and reading the
resulting order titles, with an order-sensitive assertion that mirrors the legacy
`BillingAndInvoicing.filterOrders` (`res.should.eql(results)`).

Reuse (see prefer-data-qa-selectors / migrate skill): the Angular billing iframe
scope (`estimates_helpers.billing_scope`) and the navigation timeout budget.

Selector policy: data-qa first. The Angular Orders page has no data-qa on the
type filter, its options, the list loader, or the payment rows, so the stable
legacy selectors are reused (`[name="type_filter"]`, `[name="bookings|...|"]`,
`.f-list-loader [aria-hidden="false"]`, `f-ellipsis-tooltip.payment-title`).
Those data-qa attributes should be added in the product code.

Waits: element/interaction waits are capped at 5s (STATE_TIMEOUT). NAV_TIMEOUT
(the Angular app navigation/render readiness after loading the Orders page) is the
only longer, justified budget. Orders indexing of API-created bookings/packages
can lag, so the assertion reloads at most twice (ORDERS_RELOAD_RETRIES) and polls
the filtered list up to 5s each attempt — a bounded eventual-consistency budget,
not a fixed sleep.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

from tests.salsa.sales.estimates.estimates_helpers import NAV_TIMEOUT, billing_scope

STATE_TIMEOUT = 5000
ORDERS_RELOAD_RETRIES = 2

TYPE_FILTER = '[name="type_filter"]'
TYPE_OPTIONS = ("bookings", "invoices", "packages", "products")
LIST_LOADER = '.f-list-loader [aria-hidden="false"]'
PAYMENT_ROW = "f-ellipsis-tooltip.payment-title"


def _app_base(context: dict) -> str:
    return (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")


def _goto_orders(page: Page, context: dict):
    """Load a fresh Orders list view and return the Angular billing scope."""
    page.goto(f"{_app_base(context)}/app/payments/orders", wait_until="domcontentloaded")
    scope = billing_scope(page)
    # NAV_TIMEOUT: wait for the Angular Orders page to finish rendering its type
    # filter (navigation readiness signal), not an element-interaction wait.
    scope.locator(TYPE_FILTER).first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    return scope


def _wait_list_settled(page: Page, scope) -> None:
    """Wait for the list loader to clear so reads are not taken mid-fetch."""
    loader = scope.locator(LIST_LOADER)
    try:
        if loader.count() > 0:
            loader.first.wait_for(state="hidden", timeout=STATE_TIMEOUT)
    except Exception:
        pass


def _apply_type_filter(page: Page, scope, types: list[str]) -> None:
    """Open the type filter, clear all payable types, enable `types`, then close.

    Mirrors legacy `filterByPaymentType`: clear all -> enable requested -> Escape."""
    dropdown = scope.locator(TYPE_FILTER).first
    dropdown.wait_for(state="visible", timeout=STATE_TIMEOUT)
    dropdown.click(timeout=STATE_TIMEOUT)

    scope.locator(f'[name="{TYPE_OPTIONS[0]}"]').first.wait_for(
        state="visible", timeout=STATE_TIMEOUT
    )

    for name in TYPE_OPTIONS:
        option = scope.locator(f'[name="{name}"]').first
        try:
            if option.get_attribute("selected") is not None:
                option.click(timeout=STATE_TIMEOUT)
        except Exception:
            continue

    for name in types:
        option = scope.locator(f'[name="{name}"]').first
        if option.get_attribute("selected") is None:
            option.click(timeout=STATE_TIMEOUT)

    page.keyboard.press("Escape")


def _read_order_titles(scope) -> list[str]:
    rows = scope.locator(PAYMENT_ROW)
    return [(text or "").strip() for text in rows.all_inner_texts()]


def assert_orders_filtered(
    page: Page, context: dict, types: list[str], expected: list[str]
) -> None:
    """Filter Orders by payable `types` and assert the titles equal `expected` (ordered).

    Order matters: the legacy assertion used `should.eql`, so package-then-booking
    ordering is preserved. Reloads at most ORDERS_RELOAD_RETRIES times to absorb
    Orders indexing lag of API-created bookings/packages."""
    last_seen: list[str] = []
    for attempt in range(ORDERS_RELOAD_RETRIES + 1):
        scope = _goto_orders(page, context)
        _apply_type_filter(page, scope, types)
        _wait_list_settled(page, scope)

        deadline = time.monotonic() + STATE_TIMEOUT / 1000
        while time.monotonic() < deadline:
            last_seen = _read_order_titles(scope)
            if last_seen == expected:
                return
            page.wait_for_timeout(300)

        if attempt < ORDERS_RELOAD_RETRIES:
            page.wait_for_timeout(1000)

    raise AssertionError(
        f"Orders filtered by {types}: expected {expected}, got {last_seen}"
    )
