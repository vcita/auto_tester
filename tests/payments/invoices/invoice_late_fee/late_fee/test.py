from playwright.sync_api import Page

from tests.payments.invoices.invoice_billing_api import (
    assert_jobber_execution,
    create_invoice_via_api,
    next_month_day,
    trigger_jobber_execution,
)
from tests.payments.invoices.invoice_billing_ui import assert_invoice_page

FAST_UI_TIMEOUT = 5000
LATE_FEE_EVENT = "add_invoice_late_fee"


def test_late_fee(page: Page, context: dict) -> None:
    page.set_default_timeout(FAST_UI_TIMEOUT)
    page.set_default_navigation_timeout(20000)

    due_date = next_month_day(10)
    print("  Step 1: Create invoice 'new_invoice' via API (late fee enabled)")
    invoice = create_invoice_via_api(
        context, title="new_invoice", client_id=context["created_client_id"],
        address="blablablabla",
        items=[{"title": context["invoice_service_name"], "amount": "100", "quantity": 1}],
        due_date=due_date, enable_late_fee=True,
    )
    invoice_id = invoice["id"]

    print("  Step 2: Assert invoice ISSUED at $100.00, subject to late fees")
    assert_invoice_page(
        page, context, title="new_invoice", number=1, client="first last",
        state="ISSUED", amount="$100.00", late_fee="Subject to late fees",
        invoice_id=invoice_id,
    )

    print("  Step 3: Assert pending add_invoice_late_fee jobber execution (day 15)")
    assert_jobber_execution(
        context, event_name=LATE_FEE_EVENT, status="pending",
        expected_date=next_month_day(15).strftime("%Y-%m-%d"),
    )

    print("  Step 4: Trigger the add_invoice_late_fee jobber execution")
    trigger_jobber_execution(context, LATE_FEE_EVENT)

    print("  Step 5: Assert invoice total becomes $110.00 (late fee applied)")
    assert_invoice_page(
        page, context, title="new_invoice", number=1, client="first last",
        state="ISSUED", amount="$110.00", late_fee="Subject to late fees",
        invoice_id=invoice_id, force_reload=True,
    )
