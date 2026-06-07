"""UI flows + assertions for the invoice billing migration (VCITA2-13900).

Drives the same POV itemizable wizard the estimates tests use (reused from
tests/sales/estimates/estimates_helpers), plus invoice-specific actions the
legacy invoiceAndEstimateDialogs / invoice / billingAndInvoicing page objects
covered: create+send invoice with new/existing items, copy invoice, the invoice
detail assertions (incl. late-fee caption), and the orders-list search.
"""
import re
import time

from playwright.sync_api import Page

from tests.account_api import account_request
from tests.sales.estimates.estimates_helpers import (
    add_custom_item,
    add_existing_item,
    billing_scope,
    set_billing_address,
    set_title,
    wizard_scope,
)

UI_TIMEOUT = 5000
# Bounded waits above the 5s UI cap for known async points (not flaky-selector masks),
# matching the accepted estimates_helpers / eu_strict_invoices precedents:
NAV_TIMEOUT = 20000   # angularjs iframe + Vue wizard iframe (re)mount on navigation
STATE_TIMEOUT = 15000  # invoice/orders eventual consistency (issue + list indexing)
POLL = 0.5

ORDER_ROW = "f-ellipsis-tooltip.payment-title"


def _app_base(page: Page) -> str:
    match = re.match(r"(https?://[^/]+)", page.url)
    return match.group(1) if match else ""


def open_orders(page: Page):
    page.goto(f"{_app_base(page)}/app/payments/orders", wait_until="domcontentloaded")
    billing = billing_scope(page)
    billing.get_by_role("button", name="New").first.wait_for(state="visible", timeout=NAV_TIMEOUT)
    return billing


def _select_client(page: Page, billing, client_name: str) -> None:
    """Select a client in the invoice client picker.

    The picker renders inside the angularjs frame; its result rows highlight the
    matched text (wrapped in markup) which breaks text-node matching, so select via
    keyboard (type -> ArrowDown -> Enter) like the proven create_invoice picker, then
    fall back to clicking a matching client row."""
    dialog = billing.get_by_role("dialog", name=re.compile("Invoice"))
    if dialog.count() == 0:
        dialog = billing.get_by_role("dialog")
    scope = dialog.first if dialog.count() > 0 else billing

    search = scope.locator("input").first
    search.wait_for(state="visible", timeout=UI_TIMEOUT)
    search.click()
    search.fill("")
    search.type(client_name, delay=15)

    row = scope.get_by_role("button").filter(has_text=re.compile(re.escape(client_name), re.I))
    if row.count() == 0:
        row = scope.get_by_text(client_name)
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if row.count() > 0 and row.first.is_visible():
            break
        time.sleep(POLL)

    try:
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        scope.wait_for(state="hidden", timeout=UI_TIMEOUT)
        return
    except Exception:
        pass

    if row.count() > 0 and row.first.is_visible():
        row.first.click()
        return
    raise AssertionError(f"Client picker never showed candidate: {client_name}")


def open_new_invoice(page: Page, client_name: str):
    """Open the new-invoice wizard for a client (Billing > New > Invoice). Returns (billing, wizard)."""
    billing = open_orders(page)
    new_button = billing.get_by_role("button", name="New")
    new_button.first.click()
    invoice_item = billing.get_by_role("menuitem", name="Invoice")
    invoice_item.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    invoice_item.first.click()
    _select_client(page, billing, client_name)
    wizard = wizard_scope(billing)
    wizard.locator('[data-qa="itemizable-details-header"]').first.wait_for(
        state="visible", timeout=NAV_TIMEOUT
    )
    return billing, wizard


def _handle_first_invoice_setup(billing) -> None:
    """A fresh account shows the first-invoice numbering dialog on first send; accept the
    default (#0000001) so numbering starts at 1, mirroring the legacy default path."""
    dialog = billing.locator('[data-qa="first-invoice-setup-dialog"]')
    try:
        dialog.first.wait_for(state="visible", timeout=2000)
    except Exception:
        return
    confirm = billing.get_by_role("button", name=re.compile(r"^(Save|Confirm|Continue|OK|Done)$", re.I))
    if confirm.count() > 0:
        confirm.first.click(timeout=UI_TIMEOUT)
        dialog.first.wait_for(state="hidden", timeout=UI_TIMEOUT)


def send_invoice(page: Page, billing, wizard) -> None:
    """Issue the invoice via the wizard primary action (legacy 'sends' -> ISSUED)."""
    send = wizard.locator('[data-qa="itemizable-dialog-main"]')
    if send.count() == 0:
        send = wizard.get_by_role("button", name=re.compile(r"^Send", re.I))
    send.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    send.first.click()
    _handle_first_invoice_setup(billing)
    page.wait_for_url("**/app/invoices/**", timeout=NAV_TIMEOUT, wait_until="domcontentloaded")


def create_and_send_invoice(page: Page, context: dict, *, name: str, client_name: str,
                            billing_address: str | None = None,
                            new_items: list[dict] | None = None,
                            existing_items: list[str] | None = None) -> None:
    """Create + send an invoice with new (custom) and/or existing items via the UI."""
    _, wizard = open_new_invoice(page, client_name)
    set_title(wizard, name)
    for item in existing_items or []:
        add_existing_item(wizard, item)
    for item in new_items or []:
        taxes = item.get("taxes") or []
        tax = taxes[0] if taxes else {}
        add_custom_item(
            wizard, item["product_name"], item["price"],
            description=item.get("description", ""),
            tax_name=tax.get("name", ""), tax_rate=str(tax.get("rate", "13")),
            save_item=bool(item.get("save_item")),
        )
    if billing_address:
        set_billing_address(wizard, billing_address)
    send_invoice(page, billing_scope(page), wizard)


def copy_invoice(page: Page, client_name: str) -> None:
    """Copy the newest order's invoice to a client (open first order > Copy invoice > send)."""
    billing = open_orders(page)
    first_row = billing.locator(f"{ORDER_ROW} a, a {ORDER_ROW}").first
    if first_row.count() == 0:
        first_row = billing.locator("md-list a, [role='list'] a").first
    first_row.wait_for(state="visible", timeout=NAV_TIMEOUT)
    first_row.click()
    page.wait_for_url("**/app/invoices/**", timeout=NAV_TIMEOUT, wait_until="domcontentloaded")

    billing = billing_scope(page)
    more = billing.locator('f-entity-actions .actions .button-container:last-child button')
    if more.count() == 0:
        more = billing.get_by_role("button", name=re.compile(r"more|actions", re.I))
    more.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    more.first.click()
    copy_option = billing.get_by_text("Copy invoice", exact=False)
    copy_option.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    copy_option.first.click()

    _select_client(page, billing, client_name)
    wizard = wizard_scope(billing)
    wizard.locator('[data-qa="itemizable-details-header"]').first.wait_for(
        state="visible", timeout=NAV_TIMEOUT
    )
    send_invoice(page, billing_scope(page), wizard)


def _find_invoice(context: dict, title: str) -> dict:
    """Return the newest invoice whose title == `title` (polls for indexing lag)."""
    deadline = time.monotonic() + STATE_TIMEOUT / 1000
    while True:
        response = account_request(context, "GET", "/platform/v1/invoices?per_page=100")
        data = response.get("data") or response
        invoices = data.get("invoices") if isinstance(data, dict) else data
        matches = [i for i in (invoices or []) if i.get("title") == title]
        if matches:
            matches.sort(key=lambda i: i.get("created_at") or "", reverse=True)
            return matches[0]
        if time.monotonic() >= deadline:
            raise AssertionError(f"Invoice title={title!r} not found via API")
        time.sleep(POLL)


def _page_text(page: Page) -> str:
    parts = []
    for frame in page.frames:
        try:
            parts.append(frame.locator("body").inner_text(timeout=UI_TIMEOUT))
        except Exception:
            continue
    return "\n".join(parts)


def assert_invoice_page(page: Page, context: dict, *, title: str, number: int, client: str,
                        state: str, amount: str, late_fee: str | None = None,
                        invoice_id: str | None = None, force_reload: bool = False) -> None:
    """Assert the invoice detail shows name/client/state/amount (+late fee).

    The displayed name is `{title} #{number:07d}` (numbering is deterministic on the
    fresh isolated account). If we are not already on that invoice's page (or
    `force_reload` is set, e.g. after the amount changed server-side), open it fresh by
    `invoice_id` when provided, else by its API id (looked up by title)."""
    display_name = f"{title} #{number:07d}"
    if force_reload or display_name not in _page_text(page):
        target_id = invoice_id or (_find_invoice(context, title).get("id"))
        page.goto(
            f"{_app_base(page)}/app/invoices/{target_id}",
            wait_until="domcontentloaded",
        )
    expected = [display_name, client, amount]
    expected_ci = [state]
    if late_fee:
        expected.append(late_fee)
    deadline = time.monotonic() + STATE_TIMEOUT / 1000
    text = ""
    while time.monotonic() < deadline:
        text = _page_text(page)
        if all(token in text for token in expected) and all(
            token.lower() in text.lower() for token in expected_ci
        ):
            return
        time.sleep(POLL)
    for token in expected:
        if token not in text:
            raise AssertionError(f"Invoice page missing {token!r} (invoice {display_name})")
    for token in expected_ci:
        if token.lower() not in text.lower():
            raise AssertionError(f"Invoice page missing state {token!r} (invoice {display_name})")


def search_orders(page: Page, expected_titles: list[str]) -> None:
    """Assert the orders list shows exactly `expected_titles` in order (legacy filterOrders)."""
    deadline = time.monotonic() + STATE_TIMEOUT / 1000
    actual: list[str] = []
    while time.monotonic() < deadline:
        open_orders(page)
        billing = billing_scope(page)
        rows = billing.locator(ORDER_ROW)
        actual = []
        for index in range(rows.count()):
            try:
                actual.append(rows.nth(index).inner_text().strip())
            except Exception:
                continue
        if actual == expected_titles:
            return
        time.sleep(POLL)
    raise AssertionError(f"Orders list mismatch.\n expected: {expected_titles}\n actual:   {actual}")
