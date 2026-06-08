# Source: tests/scheduling/events/events_list/list_states/script.md
# Migrated from automation-js/features/tempo/events-list.feature (VCITA2-13949)

from playwright.sync_api import Page

from tests.scheduling.events.events_list.events_list_helpers import (
    open_event_list,
    schedule_event_from_list,
    search_events,
)


def test_list_states(page: Page, context: dict) -> None:
    """Events list page: empty state, one SCHEDULED result, two results
    (SCHEDULED + COMPLETED), then the COMPLETED state filter."""
    seeded = context["events_list"]
    r2p = seeded["r2p"]["name"]
    daf = seeded["daf"]["name"]

    print("  Step 1: Empty state - search with no results")
    open_event_list(page)
    rows = search_events(page, [])
    assert rows == [], f"expected empty events list, got {rows}"

    print(f"  Step 2: Schedule '{r2p}' from the list -> SCHEDULED")
    schedule_event_from_list(page, r2p)
    expected_one = [f"{r2p} SCHEDULED"]
    rows = search_events(page, expected_one)
    assert rows == expected_one, f"expected {expected_one}, got {rows}"

    print(f"  Step 3: Schedule '{daf}' in the previous month -> COMPLETED (both shown)")
    schedule_event_from_list(page, daf, past_month=True)
    expected_two = [f"{r2p} SCHEDULED", f"{daf} COMPLETED"]
    rows = search_events(page, expected_two)
    assert rows == expected_two, f"expected {expected_two}, got {rows}"

    print("  Step 4: Filter by COMPLETED -> only the daf event")
    expected_filtered = [f"{daf} COMPLETED"]
    rows = search_events(page, expected_filtered, completed_filter=True)
    assert rows == expected_filtered, f"expected {expected_filtered}, got {rows}"

    print("  [OK] events list empty / one / two / filtered verified")
