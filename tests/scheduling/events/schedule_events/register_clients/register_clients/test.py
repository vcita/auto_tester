# Source: tests/scheduling/events/schedule_events/register_clients/register_clients/script.md
# Migrated from automation-js/features/tempo/scheduling-events.feature scenario 1 (VCITA2-14026)

import re
from datetime import datetime

from playwright.sync_api import Page

from tests.scheduling.events.schedule_events.schedule_events_ui import (
    assert_cp_conversation_title,
    read_event_details,
    register_clients_ui,
    schedule_event_ui,
)


def _next_month_name() -> str:
    today = datetime.now()
    month_index = today.month % 12 + 1
    year = today.year + (1 if today.month == 12 else 0)
    return datetime(year, month_index, 10).strftime("%B")


def test_register_clients(page: Page, context: dict) -> None:
    """Schedule a require-to-pay event from the back office (next month, assigned to
    user_staff), assert its details, register two clients, assert the attendee list, and
    assert the registered client's client-portal "Event Registration" conversation."""
    seeded = context["schedule_events"]
    service_name = seeded["service"]["name"]
    clients = seeded["clients"]

    print("  Step 1: Schedule event from back office (next month day 10, user_staff)")
    event_uid = schedule_event_ui(page, context, service_name, "user_staff")
    context["schedule_events"]["event_uid"] = event_uid

    print("  Step 2: Assert event instance details")
    details = read_event_details(page, context, event_uid)
    assert details["event_name"] == service_name, (
        f"event name: expected {service_name!r}, got {details['event_name']!r}")
    assert details["event_location"] == "TLV", (
        f"location: expected 'TLV', got {details['event_location']!r}")
    assert details["event_state"] == "SCHEDULED", (
        f"state: expected 'SCHEDULED', got {details['event_state']!r}")

    next_month = _next_month_name()
    assert next_month in details["event_date_text"] and "10" in details["event_date_text"], (
        f"date: expected {next_month} day 10 in {details['event_date_text']!r}")

    summary = details["attendance_summary"]
    assert "0" in summary and "2" in summary, (
        f"attendance summary: expected '0/ 2 Registered', got {summary!r}")

    more = " | ".join(details["more_details"])
    for expected in ("$100.00", "Available on service menu", "user_staff"):
        assert expected in more, f"more-details missing {expected!r}: {more!r}"

    assert details["attendees_info"] == [], (
        f"expected no attendees before registration, got {details['attendees_info']!r}")

    print("  Step 3: Register two clients")
    register_clients_ui(page, context, event_uid, list(clients))

    print("  Step 4: Assert both clients are attendees")
    after = read_event_details(page, context, event_uid)
    actual_names = {re.sub(r"\s+", " ", n).strip().lower() for n in after["attendees_info"]}
    expected_names = {n.lower() for n in clients}
    assert expected_names.issubset(actual_names), (
        f"attendees: expected {expected_names}, got {actual_names}")

    print("  Step 5: Assert client-portal registration conversation")
    silvan_token = clients["silvan goodbye"]["token"]
    assert_cp_conversation_title(
        page, context, silvan_token, f"Event Registration: {service_name}"
    )

    print("  [OK] schedule event + register multiple clients verified")
