# Source: tests/scheduling/events/schedule_events/unregister_pos/unregister_pos/script.md
# Migrated from automation-js/features/tempo/scheduling-events.feature scenario 2B (VCITA2-14026)

from playwright.sync_api import Page

from tests.tempo.scheduling.events.schedule_events.schedule_events_ui import (
    attendees_counter,
    cp_self_cancel_meeting,
    find_attendee,
    pay_for_attendee_bo,
    read_attendees,
    register_clients_ui,
    unregister_attendee_bo,
)

CANCELED_BY_CLIENT = "Canceled by client"


def _assert_attendees(page: Page, context: dict, event_uid: str, expected: list[dict],
                      refresh: bool = False) -> None:
    """Assert each expected attendee row (payment_status/state/index_per_category/comment).

    ``comment`` is checked by canceller category: ``""`` (registered), ``"Canceled by client"``
    (CP self-cancel), or ``"staff"`` (any "Canceled by <business>" back-office cancel) - this
    verifies who cancelled without hard-coding the rendered staff/business display name.
    ``refresh`` re-navigates first to observe an out-of-band (client-portal) change."""
    actual = read_attendees(page, context, event_uid, refresh=refresh)
    for row in expected:
        got = find_attendee(actual, row["name"])
        for field in ("payment_status", "state", "index_per_category"):
            assert got[field] == row[field], (
                f"{row['name']} {field}: expected {row[field]!r}, got {got[field]!r} "
                f"(full row {got})")
        expected_comment = row["comment"]
        if expected_comment == "":
            assert got["comment"] == "", f"{row['name']} expected no comment, got {got['comment']!r}"
        elif expected_comment == CANCELED_BY_CLIENT:
            assert got["comment"] == CANCELED_BY_CLIENT, (
                f"{row['name']} comment: expected {CANCELED_BY_CLIENT!r}, got {got['comment']!r}")
        else:  # staff/business back-office cancel
            assert got["comment"].startswith("Canceled by") and got["comment"] != CANCELED_BY_CLIENT, (
                f"{row['name']} comment: expected a staff 'Canceled by ...', got {got['comment']!r}")


def test_unregister_pos(page: Page, context: dict) -> None:
    """Register three clients, unregister one from the back office and one from the client
    portal, then pay for the last attendee through Point of Sale - asserting the attendee
    table (registered/unregistered, paid/unpaid, per-category index) at each stage."""
    seeded = context["schedule_events"]
    event_uid = seeded["event_uid"]
    clients = seeded["clients"]

    print("  Step 1: Register silvan, judi, nir to the event")
    register_clients_ui(page, context, event_uid,
                        ["silvan goodbye", "judi babish-moshe", "nir karpin"])

    print("  Step 2: Assert 3 attendees, all unpaid + registered")
    assert attendees_counter(page, context, event_uid) == 3, "expected 3 attendees after registration"
    _assert_attendees(page, context, event_uid, [
        {"name": "nir karpin", "payment_status": "unpaid", "state": "registered",
         "index_per_category": 1, "comment": ""},
        {"name": "judi babish-moshe", "payment_status": "unpaid", "state": "registered",
         "index_per_category": 2, "comment": ""},
        {"name": "silvan goodbye", "payment_status": "unpaid", "state": "registered",
         "index_per_category": 3, "comment": ""},
    ])

    print("  Step 3: Unregister judi from the back office")
    unregister_attendee_bo(page, context, event_uid, "judi babish-moshe")
    _assert_attendees(page, context, event_uid, [
        {"name": "nir karpin", "payment_status": "unpaid", "state": "registered",
         "index_per_category": 1, "comment": ""},
        {"name": "silvan goodbye", "payment_status": "unpaid", "state": "registered",
         "index_per_category": 2, "comment": ""},
        {"name": "judi babish-moshe", "payment_status": "unpaid", "state": "unregistered",
         "index_per_category": 3, "comment": "staff"},
    ])
    assert attendees_counter(page, context, event_uid) == 2, "expected 2 attendees after BO unregister"

    print("  Step 4: silvan self-cancels the registration from the client portal")
    cp_self_cancel_meeting(page, context, clients["silvan goodbye"]["token"], seeded["service"]["name"])
    _assert_attendees(page, context, event_uid, [
        {"name": "nir karpin", "payment_status": "unpaid", "state": "registered",
         "index_per_category": 1, "comment": ""},
        {"name": "silvan goodbye", "payment_status": "unpaid", "state": "unregistered",
         "index_per_category": 2, "comment": CANCELED_BY_CLIENT},
        {"name": "judi babish-moshe", "payment_status": "unpaid", "state": "unregistered",
         "index_per_category": 3, "comment": "staff"},
    ], refresh=True)

    print("  Step 5: Pay nir's $100 through Point of Sale")
    pay_for_attendee_bo(page, context, event_uid, "nir karpin", "100", pos=True)
    _assert_attendees(page, context, event_uid, [
        {"name": "silvan goodbye", "payment_status": "unpaid", "state": "unregistered",
         "index_per_category": 1, "comment": CANCELED_BY_CLIENT},
        {"name": "judi babish-moshe", "payment_status": "unpaid", "state": "unregistered",
         "index_per_category": 2, "comment": "staff"},
        {"name": "nir karpin", "payment_status": "paid", "state": "registered",
         "index_per_category": 1, "comment": ""},
    ])

    print("  [OK] unregister from BO + CP and POS payment verified")
