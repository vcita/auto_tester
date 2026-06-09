"""CP scheduling with taxes (VCITA2-14008).

Migrated from payment-setups.feature scenario "CP Scheduling with taxes": the default tax and
the taxed ``suggest2pay`` service come from ``_setup``; this test grabs the service public
link, books it as an anonymous client through the client-portal scheduler (verifying the
calendar shows +Tax at $100.00), then verifies the client-portal meeting page shows the price
and tax.
"""

from playwright.sync_api import Page

from tests.scheduling.payment_setups.cp_scheduling_helpers import (
    assert_calendar_summary,
    assert_meeting,
    book_appointment,
    grab_service_link,
    open_meeting,
    open_scheduler,
)


def test_cp_scheduling_taxes(page: Page, context: dict) -> None:
    service_name = context["ps"]["service"]["name"]

    link = grab_service_link(page, service_name)
    print(f"  [OK] Grabbed public link for {service_name}")

    open_scheduler(page, link)
    assert_calendar_summary(page, service_name=service_name, tax="+Tax", price="$100.00")
    print("  [OK] Scheduler calendar shows the service with +Tax at $100.00")

    book_appointment(page, first_name="jimmy", email=f"test8+{context['ps']['service']['id']}@vmeetme.com")
    print("  [OK] Booked the appointment as an anonymous client")

    open_meeting(page, service_name)
    assert_meeting(page, meeting_name=service_name, price="$100.00", tax="+Tax")
    print("  [OK] Client-portal meeting page shows $100.00 with +Tax")
