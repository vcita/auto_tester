"""Account-scoped API helpers for the multi-booking subcategory.

Used only to resolve the back-office appointment ids of a freshly scheduled
multi-service booking (the create itself is exercised through the UI). Mirrors
the legacy `addBookingToContext` diff against the appointments list endpoint.
"""

import time

from tests.account_api import account_request, pivot_uid


def list_appointments(context: dict) -> list[dict]:
    """Return the account's appointments (id + title + state)."""
    response = account_request(
        context,
        "GET",
        f"/platform/v1/scheduling/appointments?business_id={pivot_uid(context)}",
    )
    return response.get("data", {}).get("appointments", [])


def appointment_ids(context: dict) -> set[str]:
    return {str(a.get("id")) for a in list_appointments(context) if a.get("id")}


def appointments_by_id(context: dict) -> dict[str, dict]:
    return {str(a.get("id")): a for a in list_appointments(context) if a.get("id")}


def wait_for_new_appointments(
    context: dict,
    before: set[str],
    *,
    expected: int,
    attempts: int = 10,
    interval_seconds: float = 1.5,
) -> dict[str, dict]:
    """Poll the appointments list until `expected` new ids appear after `before`.

    The appointments index lags the UI submit (legacy addBookingToContext retried
    for the same reason), so this polls instead of reading once.
    """
    latest: dict[str, dict] = {}
    for _ in range(attempts):
        latest = appointments_by_id(context)
        new_ids = set(latest) - before
        if len(new_ids) >= expected:
            return {aid: latest[aid] for aid in new_ids}
        time.sleep(interval_seconds)
    new_ids = set(latest) - before
    raise AssertionError(
        f"Expected {expected} new appointments, found {len(new_ids)} (before={len(before)})"
    )
