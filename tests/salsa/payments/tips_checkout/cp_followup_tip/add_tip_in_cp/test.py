# Migrated from automation-js/features/salsa/tips.feature (VCITA2-13899)
# Source: tests/payments/tips_checkout/cp_followup_tip/add_tip_in_cp/script.md

from playwright.sync_api import Page

from tests.salsa.payments.tips_checkout.tips_checkout_cp import add_meeting_followup_tip


def test_add_tip_in_cp(page: Page, context: dict) -> None:
    """Client adds a 66% follow-up tip to a paid past meeting from the client portal."""
    store = context["tips_checkout"]
    client = store["client"]
    meeting_name = store["require_meeting_name"]

    print("  Add a 66% follow-up tip on the paid 'require' meeting via CP")
    add_meeting_followup_tip(page, context, portal_token=client["portal_token"],
                             meeting_name=meeting_name, tip_option="66%",
                             expected_amount="$66.00")
