# Migrated from automation-js/features/salsa/tips.feature (VCITA2-13899)
# Source: tests/payments/tips_checkout/event_followup_tip/record_tip/script.md

from playwright.sync_api import Page

from tests.payments.tips_checkout.tips_checkout_bo import (
    add_followup_tip,
    assert_payment_page_with_tip,
    open_paid_event_order,
)


def test_record_tip(page: Page, context: dict) -> None:
    """Add a Custom $5 record follow-up tip to a paid event attendance (BO)."""
    store = context["tips_checkout"]
    event_name = store["event_name"]

    print(f"  Open paid '{event_name}' attendance order and add a Custom $5 record tip")
    open_paid_event_order(page, context, event_name)
    add_followup_tip(page, context, tip_option="Custom", payment_type="record", tip_amount="5")

    assert_payment_page_with_tip(page, context, {
        "search": "first",
        "client_name": "first last",
        "name": f"Tip for {event_name}",
        "amount": "$5.00",
        "type": "Cash",
        "items": event_name,
        "tip": "$5.00",
    })
