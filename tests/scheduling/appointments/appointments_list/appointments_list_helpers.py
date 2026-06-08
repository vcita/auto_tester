"""UI + API helpers for the appointments-list migration (VCITA2-13953).

The appointments list page is the same Vue booking-list UI as the events list page,
mounted at ``/app/appointment-list``: a Vue app (``#vue_iframe_layout``) nested inside the
Angular frontage iframe (``iframe[title="angularjs"]``). The filter panel, list rows,
status, empty state and export action all render in the Vue (inner) iframe. The
client-portal "Appointment confirmed" conversation check opens the vitrage ``cp_iframe``.

Selectors verified against the current frontage source (BookingsPage.vue, BookingList.vue,
BookingListItemDesktop.vue, BookingStatus.vue, BookingFilter.vue, FilterPanel.vue,
FilterSearch.vue, BookingActionBar.vue, ExportAppointmentsDialog.vue).
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timedelta, timezone

from playwright.sync_api import Download, Page

from tests.account_api import account_request, pivot_uid
from tests.scheduling.appointments.appointment_helpers import UI_TIMEOUT

APPOINTMENT_LIST_PATH = "/app/appointment-list"
_SETTLE_MS = 250
# CP confirmation activity posts asynchronously (realtime); bounded ≤5s readiness poll.
CP_POLL_TIMEOUT_MS = 5_000
# Opening the client portal is a full cross-domain app load (vitrage shell + cp_iframe +
# Vue dashboard), so it gets a page-readiness budget analogous to login waiting for the
# dashboard (not an element wait) — same 15s budget proven in tests/reviews/reviews_cp_ui.
CP_LOAD_TIMEOUT_MS = 15_000

CP_DASHBOARD_READY = ".quick-actions, .matter-picker"
CHAT_BUTTON = '[data-qa="headerChatBtn"]'
CONVERSATION_TITLE = '[data-qa="bubble-header"]'


# --------------------------------------------------------------------------- #
# Appointment start-time helpers (API setup; mirror legacy meeting_date tokens)
# --------------------------------------------------------------------------- #
def previous_month_appointment_start_time(day: int = 10, hour: int = 10) -> str:
    """Start time on day ``day`` of the previous month at ``hour`` UTC.

    Mirrors the legacy ``previous_month_10`` token: the instance lands in the past so the
    booking renders COMPLETED in the list.
    """
    now = datetime.now(timezone.utc)
    first_of_this_month = now.replace(day=1, hour=hour, minute=0, second=0, microsecond=0)
    last_of_prev_month = first_of_this_month - timedelta(days=1)
    start = last_of_prev_month.replace(day=day, hour=hour, minute=0, second=0, microsecond=0)
    return start.isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------------- #
# Service persistence read-back (independent GET)
# --------------------------------------------------------------------------- #
def verify_service_persisted(context: dict, service_id: str, name: str) -> None:
    """A 200 on POST can silently drop fields, so confirm the service is actually listed
    before the UI relies on it (mirrors the legacy get_services read-back)."""
    response = account_request(
        context, "GET", f"/platform/v1/services?business_id={pivot_uid(context)}"
    )
    services = (response.get("data") or {}).get("services") or response.get("services") or []
    for service in services:
        if (service.get("id") or service.get("uid")) == service_id:
            return
    raise AssertionError(
        f"Service {name!r} ({service_id}) not found in services read-back; "
        f"got {[s.get('name') for s in services]}"
    )


# --------------------------------------------------------------------------- #
# Appointment list page (Vue inside Angular iframe)
# --------------------------------------------------------------------------- #
def _frames(page: Page):
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator("#vue_iframe_layout")
    return outer, inner


def _app_base(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context; cannot open the appointments list")
    return base


def open_appointment_list(page: Page, context: dict):
    """Navigate to the appointments list page and wait until the filter search box is
    ready. Returns (outer, inner) frame locators. Retries once (reload) on a render race.

    The app URL is built from ``context["base_url"]`` (not the current page URL) so it is
    correct even after the client-portal check navigated to the vitrage host. Idempotent:
    if already on the appointments list page it does not re-navigate (clearing or applying
    filters re-fetches bookings from the server, so API-created appointments appear without
    a full reload).
    """
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            if APPOINTMENT_LIST_PATH not in page.url:
                page.goto(
                    f"{_app_base(context)}{APPOINTMENT_LIST_PATH}",
                    wait_until="domcontentloaded",
                    timeout=UI_TIMEOUT,
                )
            page.wait_for_url("**/app/appointment-list**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
            page.wait_for_selector('iframe[title="angularjs"]', state="visible", timeout=UI_TIMEOUT)
            outer, inner = _frames(page)
            inner.locator('[data-qa="filter-search"]').wait_for(state="visible", timeout=UI_TIMEOUT)
            return outer, inner
        except Exception as exc:  # noqa: BLE001 - bounded retry on render race
            last_error = exc
            if attempt == 0:
                page.reload(wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    raise last_error or AssertionError("Appointments list page did not become ready")


def search_appointments(page: Page, context: dict, expected_rows: list[str], *, completed_filter: bool = False) -> list[str]:
    """Ensure the appointments list is loaded, (re)apply the search, and return the rows.

    For ``completed_filter`` the COMPLETED status filter is applied directly; otherwise the
    filters are cleared. Both trigger a server re-fetch (so API-created appointments
    appear). Status token is upper-cased so the assertion is locale/CSS independent while
    preserving which status is shown. Bounded ≤5s readiness poll for the debounced reload.
    """
    open_appointment_list(page, context)
    _, inner = _frames(page)
    if completed_filter:
        _apply_completed_filter(page, inner)
    else:
        _clear_filters(page, inner)

    actual: list[str] = []
    for _ in range(int(CP_POLL_TIMEOUT_MS / _SETTLE_MS)):
        actual = _read_rows(inner)
        if actual == expected_rows:
            return actual
        page.wait_for_timeout(_SETTLE_MS)
    return actual


def _clear_filters(page: Page, inner) -> None:
    # "Clear filters" lives in a `.button-area` with pointer-events:none, so JS click it
    # (matches the Vue click guidance for filter controls).
    clear_btn = inner.get_by_role("button", name="Clear filters")
    clear_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    clear_btn.evaluate("el => el.click()")


def _apply_completed_filter(page: Page, inner) -> None:
    # First clear any prior filter state, then check the "Completed" booking-status item.
    _clear_filters(page, inner)
    booking_filter = inner.locator(".booking-filter")
    completed = booking_filter.get_by_text(re.compile(r"^\s*completed\s*$", re.I)).first
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


# --------------------------------------------------------------------------- #
# Export
# --------------------------------------------------------------------------- #
EXPORT_ICON = ".icon-export"
_EXPORT_ACTION_SELECTORS = (
    '[data-qa="vc-footer-Extract"]',
    '[data-qa="vc-footer-Export"]',
)


def export_appointment_list(page: Page) -> Download:
    """Open the export dialog from the list action bar, confirm the export, and return the
    captured browser download (the page builds a `data:` anchor download)."""
    _, inner = _frames(page)
    export_icon = inner.locator(EXPORT_ICON).first
    export_icon.wait_for(state="visible", timeout=UI_TIMEOUT)
    export_icon.click(timeout=UI_TIMEOUT)

    confirm = _resolve_export_action(inner)
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    with page.expect_download(timeout=UI_TIMEOUT) as download_info:
        confirm.click(timeout=UI_TIMEOUT)
    return download_info.value


def _resolve_export_action(inner):
    for selector in _EXPORT_ACTION_SELECTORS:
        candidate = inner.locator(selector).first
        if candidate.count() > 0:
            return candidate
    return inner.get_by_role("button", name=re.compile(r"Extract|Export", re.I)).first


def assert_download_is_bookings(download: Download) -> None:
    name = download.suggested_filename or ""
    assert "bookings" in name.lower(), f"Expected a 'Bookings' export download, got {name!r}"


# --------------------------------------------------------------------------- #
# Client-portal "Appointment confirmed" conversation check (vitrage cp_iframe)
# --------------------------------------------------------------------------- #
def _vitrage_base(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if "app.meet2know.com" in base:
        return "https://live.meet2know.com"
    if "app.vcita.com" in base:
        return "https://live.vcita.com"
    if "app-" in base and ".external.int-eks.vchost.co" in base:
        return base.replace("https://app-", "https://vitrage-", 1)
    raise ValueError(f"Cannot derive vitrage base URL from base_url={base!r}")


def assert_cp_conversation_includes(page: Page, context: dict, client: dict, title: str) -> None:
    """Open the client portal as the client and verify the conversation includes ``title``.

    Mirrors the legacy `conversation with client ... in client portal includes title ...`:
    open `?client_jwt=<token>`, click the chat button, and poll the conversation titles
    (`[data-qa="bubble-header"]`). The confirmation posts asynchronously, so poll ≤5s.
    """
    token = client.get("token")
    if not token:
        raise ValueError("Client portal token missing; cannot open the client portal")
    url = f"{_vitrage_base(context)}/site/{pivot_uid(context)}/action?client_jwt={token}"
    page.goto(url, wait_until="domcontentloaded", timeout=UI_TIMEOUT)

    if _wait_cp_frame(page, CP_DASHBOARD_READY) is None:
        raise AssertionError("Client-portal dashboard (cp_iframe) did not become ready")
    chat = _wait_in_frame(page, CP_DASHBOARD_READY, CHAT_BUTTON)
    if chat is None:
        raise AssertionError("Conversation (chat) button did not appear in the client portal")
    chat.click(timeout=UI_TIMEOUT)

    deadline = time.monotonic() + CP_POLL_TIMEOUT_MS / 1000
    seen: list[str] = []
    while time.monotonic() < deadline:
        frame = _frame_with(page, CONVERSATION_TITLE)
        if frame is not None:
            titles = frame.locator(CONVERSATION_TITLE)
            seen = []
            for index in range(titles.count()):
                try:
                    text = (titles.nth(index).inner_text(timeout=1000) or "").strip()
                except Exception:  # noqa: BLE001
                    continue
                seen.append(text)
                if title in text:
                    return
        time.sleep(0.25)
    raise AssertionError(
        f"Conversation title {title!r} did not appear in the client portal. Titles seen: {seen}"
    )


def _frame_with(page: Page, selector: str):
    frame = page.frame(name="cp_iframe")
    candidates = [frame, *page.frames] if frame is not None else list(page.frames)
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            if candidate.locator(selector).count() > 0:
                return candidate
        except Exception:  # noqa: BLE001
            continue
    return None


def _wait_cp_frame(page: Page, ready_selector: str):
    deadline = time.monotonic() + CP_LOAD_TIMEOUT_MS / 1000
    while time.monotonic() < deadline:
        frame = _frame_with(page, ready_selector)
        if frame is not None:
            return frame
        time.sleep(0.2)
    return None


def _wait_in_frame(page: Page, ready_selector: str, target_selector: str):
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        frame = _frame_with(page, target_selector) or _frame_with(page, ready_selector)
        if frame is not None:
            locator = frame.locator(target_selector)
            for index in range(locator.count()):
                candidate = locator.nth(index)
                try:
                    if candidate.is_visible():
                        return candidate
                except Exception:  # noqa: BLE001
                    continue
        time.sleep(0.1)
    return None
