"""UI helpers for the events-list migration (VCITA2-13949).

The events list page is a Vue app (`#vue_iframe_layout`) nested inside the Angular
frontage iframe (`iframe[title="angularjs"]`). The "+ new event" action button lives
in the Angular actions bar (outer iframe); the create-event dialog, filter panel and
list render in the Vue iframe (inner). Selectors are verified against the current
frontage source (EventList.vue, EventDialog.vue, DatePicker.vue, BookingStatus.vue,
FilterPanel.vue, actions-bar haml).
"""

from __future__ import annotations

import re

from playwright.sync_api import Page

from tests.tempo.scheduling.appointments.appointment_helpers import UI_TIMEOUT

EVENT_LIST_PATH = "/app/event-list"
NEW_EVENT_BUTTON = '[data-qa="action-button-eventList-new_event"]'
_SETTLE_MS = 250


def _app_base(page: Page) -> str:
    if "/app/" not in page.url:
        raise ValueError(f"Cannot infer app base URL from: {page.url}")
    return page.url.split("/app/")[0]


def _frames(page: Page):
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator("#vue_iframe_layout")
    return outer, inner


def open_event_list(page: Page):
    """Navigate to the events list page and wait until the filter search box is ready.

    Returns (outer, inner) frame locators. Retries once (reload) if the Vue app does
    not render the filter panel in time.
    """
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            if EVENT_LIST_PATH not in page.url:
                page.goto(f"{_app_base(page)}{EVENT_LIST_PATH}", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
            page.wait_for_url("**/app/event-list**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
            page.wait_for_selector('iframe[title="angularjs"]', state="visible", timeout=UI_TIMEOUT)
            outer, inner = _frames(page)
            inner.locator('[data-qa="filter-search"]').wait_for(state="visible", timeout=UI_TIMEOUT)
            return outer, inner
        except Exception as exc:  # noqa: BLE001 - bounded retry on render race
            last_error = exc
            if attempt == 0:
                page.reload(wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    raise last_error or AssertionError("Events list page did not become ready")


SERVICE_SELECT = '[data-qa="service-select-input"]'
SUBMIT_BUTTON = '[data-qa="dialog-submit-button"]'


def schedule_event_from_list(page: Page, service_name: str, *, past_month: bool = False) -> None:
    """Schedule an event from the events list page via the "+ new event" button.

    Selects ``service_name`` in the event dialog; when ``past_month`` is set, moves the
    start date to the 10th of the previous month (so the instance lands in the past →
    COMPLETED). Otherwise the dialog default (near-future) is kept → SCHEDULED.

    The events-list "+ new event" button is in the Angular actions bar, but the event
    dialog renders in a separate booking Vue iframe (not the event-list frame), so the
    dialog is driven through the frame that actually contains the service select.
    """
    outer, _ = _frames(page)
    new_event_btn = outer.locator(NEW_EVENT_BUTTON)
    new_event_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    new_event_btn.click()

    dialog = _dialog_frame(page)
    _select_service(dialog, service_name)
    if past_month:
        _set_start_date_previous_month(dialog)

    submit = dialog.locator(f"{SUBMIT_BUTTON}:not([disabled])")
    submit.wait_for(state="visible", timeout=UI_TIMEOUT)
    submit.click()
    _wait_dialog_closed(page)


def _dialog_frame(page: Page):
    """Return the Vue frame that hosts the open event dialog (identified by the service
    select). The dialog is mounted in a dedicated booking iframe, separate from the
    event-list frame."""
    deadline_steps = int(UI_TIMEOUT / _SETTLE_MS)
    for _ in range(deadline_steps):
        for frame in page.frames:
            try:
                if frame.locator(SERVICE_SELECT).count() > 0:
                    return frame
            except Exception:  # noqa: BLE001 - frame may be navigating
                continue
        page.wait_for_timeout(_SETTLE_MS)
    raise AssertionError("Event dialog frame (service select) did not appear")


def _wait_dialog_closed(page: Page) -> None:
    for _ in range(int(UI_TIMEOUT / _SETTLE_MS)):
        still_open = False
        for frame in page.frames:
            try:
                if frame.locator(SUBMIT_BUTTON).count() > 0:
                    still_open = True
                    break
            except Exception:  # noqa: BLE001
                continue
        if not still_open:
            return
        page.wait_for_timeout(_SETTLE_MS)


def _select_service(dialog, service_name: str) -> None:
    # Mirrors the proven event-dialog flow (scheduling/events/schedule_event): open the
    # service combobox and pick the option by name (the fresh account has only the two
    # seeded services, so no text filtering is needed).
    combobox = dialog.get_by_role("combobox").first
    combobox.wait_for(state="visible", timeout=UI_TIMEOUT)
    combobox.click()
    dialog.get_by_role("listbox").wait_for(state="visible", timeout=UI_TIMEOUT)
    option = dialog.get_by_role("option").filter(has_text=service_name).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()


def _set_start_date_previous_month(dialog) -> None:
    start_date = dialog.locator('[data-qa="date-picker-text-input"]').first
    start_date.click()
    menu = dialog.locator(".date-picker-menu-content")
    menu.wait_for(state="visible", timeout=UI_TIMEOUT)
    # v-date-picker header buttons: [prev, next]; first = previous month.
    menu.locator(".v-date-picker-header button").first.click()
    day_btn = menu.locator(".v-date-picker-table button:visible").filter(
        has_text=re.compile(r"^\s*10\s*$")
    )
    day_btn.last.wait_for(state="visible", timeout=UI_TIMEOUT)
    day_btn.last.click()
    menu.wait_for(state="hidden", timeout=UI_TIMEOUT)


def search_events(page: Page, expected_rows: list[str], *, completed_filter: bool = False) -> list[str]:
    """Reset/apply the events-list filter, then poll the list until the rendered
    ``"<title> <STATUS>"`` rows match ``expected_rows``.

    Mirrors legacy bookingsList.searchBookings (reset via "Clear filters", apply filters,
    compare the list; empty-state → []). For the COMPLETED case the status filter is
    applied directly: the caller always reaches this after a cleared list, and clearing
    then re-filtering would fire two debounced reloads that race to an empty result.
    Status token is upper-cased so the assertion is locale/CSS independent while
    preserving which status is shown. Returns the rows actually read (for diagnostics).
    """
    _, inner = _frames(page)
    if completed_filter:
        _apply_completed_filter(page, inner)
    else:
        _clear_filters(page, inner)

    actual: list[str] = []
    # Bounded readiness poll (<=5s): the list reload is debounced, so poll for the
    # expected result rather than a single fixed wait.
    for _ in range(int(UI_TIMEOUT / _SETTLE_MS)):
        actual = _read_rows(inner)
        if actual == expected_rows:
            return actual
        page.wait_for_timeout(_SETTLE_MS)
    return actual


def _clear_filters(page: Page, inner) -> None:
    # The "Clear filters" button lives in a `.button-area` with pointer-events:none,
    # so a JS click is used (matches the Vue click guidance for filter controls).
    clear_btn = inner.get_by_role("button", name="Clear filters")
    clear_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    clear_btn.evaluate("el => el.click()")


def _apply_completed_filter(page: Page, inner) -> None:
    # The status labels render upper-cased, so match case-insensitively.
    event_filter = inner.locator(".event-filter")
    completed = event_filter.get_by_text(re.compile(r"^\s*completed\s*$", re.I)).first
    completed.wait_for(state="visible", timeout=UI_TIMEOUT)
    completed.evaluate("el => el.click()")


def _read_rows(inner) -> list[str]:
    if inner.locator(".booking-empty-state").count() > 0:
        return []
    rows = inner.locator(".booking-list-container .list-item")
    result: list[str] = []
    for i in range(rows.count()):
        row = rows.nth(i)
        title = (row.locator(".service-title").inner_text() or "").strip()
        status = (row.locator(".status-text").inner_text() or "").strip().upper()
        if title:
            result.append(f"{title} {status}".strip())
    return result
