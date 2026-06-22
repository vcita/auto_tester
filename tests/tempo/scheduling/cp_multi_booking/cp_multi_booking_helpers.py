"""Client-portal multi-booking helpers (VCITA2-14228).

Migrated from automation-js features/tempo/CP/multi-booking.feature step definitions and
ClientPortal/Scheduler page objects (scheduler.js, serviceList.js, calendar.js,
bookingSummary.js, intakeForm.js, bookingConfirmation.js, clientPortalMeeting.js,
dashboard.js) plus api/scheduling.js (enableMultiBookingViaApi, create_new_event).

The client portal renders inside the ``cp_iframe`` of the public livesite, but the livesite
shell sometimes nests it differently, so every frame is scanned for the relevant selector
(same approach as cp_scheduling_helpers). Selectors are quoted verbatim from the legacy page
objects: data-qa first, then the stable legacy CSS where the component exposes no data-qa.

Element/interaction waits are capped at 5s (UI_TIMEOUT); navigation into the livesite +
client-portal iframe uses a longer, documented readiness budget (CP_TIMEOUT) because it is a
full cross-origin livesite -> Angular -> Vue iframe load, not an element-interaction wait.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from playwright.sync_api import Page

from tests.account_api import account_request, first_staff_uid, pivot_uid
from tests.salsa.sales.estimates.estimates_helpers import CP_VITRAGE

UI_TIMEOUT = 5_000
CP_TIMEOUT = 20_000  # livesite + cp_iframe load / step transition (not an element-interaction wait)
SETTLE_MS = 250

# Livesite (public business page) action cards (Angular vitrage shell).
LIVESITE_ACTION_CARD = ".action-content"

# CP scheduler (cp_iframe).
SCHEDULER_CONTAINER = ".schedule-main"
SERVICES_CONTAINER = '[data-qa="ServiceCategoryPage"] .service-item'
SERVICE_ITEM = ".service-item"
SERVICE_TITLE = "span.service-title[data-style-id]"
ENABLED_SERVICE = ".service-item:not(.disabled-service)"
DISABLED_SERVICE = ".service-item.disabled-service"
SUMMARY_CONFIRM_BTN = ".summary-card__cta"
CALENDAR_CONTAINER = '[data-qa="ScheduleSelection"] .schedule-container'
TIME_SLOT = "button.time-slot"
CONTINUE_BTN = ".submit-button span, .summary-card__cta"
FUTURE_EVENT = ".future-events-list"

# Booking summary (multi-booking) — data-qa fields (bookingSummary.js).
SUMMARY_DURATION = '[data-qa="booking-detail-duration"]'
SUMMARY_LOCATION = '[data-qa="booking-detail-service-location"]'
SUMMARY_STAFF = '[data-qa="booking-detail-staff-name"]'
SUMMARY_START_DATE = '[data-qa="booking-detail-start-date"]'
SUMMARY_START_TIME = '[data-qa="booking-detail-start-time"]'

# Intake form (intakeForm.js).
INTAKE_FORM = '.scheduling-intake-form[data-qa="SchedulingIntakeForm"]'
INTAKE_EMAIL = "input[type='email']"
INTAKE_CONFIRM = ".submit-button span, .summary-card__cta"

# Booking confirmation (bookingConfirmation.js).
CONFIRM_CONTAINER = '[data-qa="ConfirmBooking"]'
CONFIRM_TITLE = ".text-container span.confirmation-title"

# CP dashboard + meeting page (dashboard.js, clientPortalMeeting.js).
DASHBOARD_BTN = ".business-title"
V_APPLICATION = ".v-application--wrap"
BOOKINGS_MENU = "[data-qa='client-area-menu-bookings']"
BOOKING_TITLE = ".booking-title"
MEETING_STATE = ".state.booking-state"
LINKED_BOOKING_TITLE = "[data-qa='linked-appointment-row-title']"


# --------------------------------------------------------------------------- #
# API setup helpers (prerequisites only)
# --------------------------------------------------------------------------- #
def enable_multi_booking(context: dict) -> None:
    """Enable client-portal multi booking (legacy enableMultiBookingViaApi) and read it back.

    PUT /v2/settings {allow_client_multi_booking: true}. The setting write is account-global;
    read it back so the scheduler never opens before it has taken effect.
    """
    account_request(context, "PUT", "/v2/settings", json={"allow_client_multi_booking": True})
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        response = account_request(context, "GET", "/v2/settings")
        data = response.get("data") or response
        settings = data.get("settings") or data
        if settings.get("allow_client_multi_booking") is True:
            return
        time.sleep(SETTLE_MS / 1000)
    raise AssertionError("allow_client_multi_booking did not read back as True after enabling")


def schedule_event_via_api(context: dict, service: dict, *, lead_days: int = 20) -> dict:
    """Schedule an event instance from an event service (legacy create_new_event).

    POST /v2/event_instances with the event service's interaction details. The start time is
    a future date so the event shows in the scheduler's future-event list.
    """
    start_time = datetime.now(timezone.utc) + timedelta(days=lead_days)
    start_time = start_time.replace(minute=0, second=0, microsecond=0)
    duration = int(service.get("duration") or 30)
    end_time = start_time + timedelta(minutes=duration)
    payload = {
        "title": service["name"],
        "event_service_id": service["id"],
        "interaction_type": service.get("interaction_type", "business_location"),
        "interaction_details": service.get("meeting_interaction_details", "TLV"),
        "max_attendance": service.get("max_attendance", 2),
        "start_time": start_time.isoformat().replace("+00:00", "Z"),
        "end_time": end_time.isoformat().replace("+00:00", "Z"),
        "charge_type": service.get("charge_type", "free"),
        "price": service.get("price"),
        "currency": service.get("currency", "USD"),
        "staff_id": first_staff_uid(context),
        "duration": duration,
        "padding": service.get("padding", 0),
        "display": True,
    }
    response = account_request(context, "POST", "/v2/event_instances", json=payload)
    data = response.get("data") or response
    return data.get("event_instance") or data


# --------------------------------------------------------------------------- #
# Livesite -> CP scheduler
# --------------------------------------------------------------------------- #
def schedule_now(page: Page, context: dict):
    """Open the public livesite and pick the "Schedule Now" action card.

    Mirrors legacy ``Livesite(account).goto().clickAnAction("Schedule Now")``: go to
    ``/site/<pivot>``, click the action card whose text is "Schedule Now", and return the
    CP scheduler frame (services page) once it renders inside the cp_iframe.
    """
    url = f"{CP_VITRAGE}/site/{pivot_uid(context)}"
    page.goto(url, wait_until="domcontentloaded", timeout=CP_TIMEOUT)
    card = page.locator(LIVESITE_ACTION_CARD, has_text="Schedule Now").first
    card.wait_for(state="visible", timeout=CP_TIMEOUT)
    card.click(timeout=UI_TIMEOUT)
    frame = _cp_frame_with(page, SERVICES_CONTAINER, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("CP scheduler services page did not load after Schedule Now")
    return frame


# --------------------------------------------------------------------------- #
# CP scheduler services page
# --------------------------------------------------------------------------- #
def _services_frame(page: Page):
    frame = _cp_frame_with(page, SERVICES_CONTAINER, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("CP scheduler services page is not present")
    return frame


def _service_row(frame, service_name: str):
    """Return the .service-item row whose title is exactly ``service_name``.

    Matches on the title span (serviceList.js _getServiceName) so substring names
    (service1 vs service6) do not cross-match.
    """
    return frame.locator(SERVICE_ITEM).filter(
        has=frame.get_by_text(service_name, exact=True)
    ).first


def select_services(page: Page, service_names: list[str]) -> None:
    """Select one or more services, then click the summary confirm CTA (legacy
    ServiceList.selectServices: click each service title, then summaryConfirmButton)."""
    frame = _services_frame(page)
    _wait_service_titles_loaded(frame)
    for name in service_names:
        title = frame.locator(SERVICE_TITLE, has_text=name).first
        title.wait_for(state="visible", timeout=UI_TIMEOUT)
        title.click(timeout=UI_TIMEOUT)
    confirm = frame.locator(SUMMARY_CONFIRM_BTN).first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click(timeout=UI_TIMEOUT)


def toggle_service(page: Page, service_name: str) -> None:
    """Click a single service title to select/deselect it (legacy ServiceList.selectService,
    which is the same click used for both select and deselect)."""
    frame = _services_frame(page)
    _wait_service_titles_loaded(frame)
    title = frame.locator(SERVICE_TITLE, has_text=service_name).first
    title.wait_for(state="visible", timeout=UI_TIMEOUT)
    title.click(timeout=UI_TIMEOUT)


def assert_services_disabled_state(page: Page, expected: dict[str, bool]) -> None:
    """Assert each service name maps to its expected disabled state (legacy
    "scheduler services page displays" with the disabled column).

    ``expected`` maps service title -> True (disabled) / False (enabled). A row is disabled
    when it carries ``.disabled-service`` (serviceList.js disabledService selector).
    """
    frame = _services_frame(page)
    _wait_service_titles_loaded(frame)
    for name, should_be_disabled in expected.items():
        row = _service_row(frame, name)
        row.wait_for(state="visible", timeout=UI_TIMEOUT)
        klass = (row.get_attribute("class", timeout=UI_TIMEOUT) or "")
        is_disabled = "disabled-service" in klass
        if is_disabled != should_be_disabled:
            raise AssertionError(
                f"service {name!r}: expected disabled={should_be_disabled}, "
                f"got disabled={is_disabled} (class={klass!r})"
            )


def _wait_service_titles_loaded(frame) -> None:
    """Wait until every service title has rendered text (legacy _servicesTitlesLoaded)."""
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        titles = frame.locator(SERVICE_TITLE)
        count = titles.count()
        if count > 0:
            texts = [(titles.nth(i).inner_text(timeout=1_000) or "").strip() for i in range(count)]
            if all(texts):
                return
        time.sleep(SETTLE_MS / 1000)
    raise AssertionError("Scheduler service titles did not finish loading")


# --------------------------------------------------------------------------- #
# Calendar (default timeslot) -> multi-booking summary
# --------------------------------------------------------------------------- #
def pick_default_timeslot_and_continue(page: Page) -> None:
    """On the calendar page pick the first available timeslot and click the multi-booking
    confirm CTA (legacy CPCalendar._selectDefaultTimeSlot + continueToIntake(is_multi_booking),
    which clicks ``.summary-card__cta`` for multi booking)."""
    frame = _cp_frame_with(page, TIME_SLOT, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("No timeslot was offered by the scheduler calendar")
    frame.locator(TIME_SLOT).first.click(timeout=UI_TIMEOUT)
    confirm = _cp_frame_with(page, SUMMARY_CONFIRM_BTN, timeout=CP_TIMEOUT)
    if confirm is None:
        raise AssertionError("Multi-booking calendar confirm CTA did not appear")
    confirm.locator(SUMMARY_CONFIRM_BTN).first.click(timeout=UI_TIMEOUT)


def assert_summary_component(
    page: Page, *, location: str, duration: str, providing_staff: str
) -> None:
    """Assert the multi-booking summary component (legacy "summary component displays").

    Checks the three value fields (location/duration/staff) and that the date/time fields are
    present (legacy table uses ``default`` for date/time = existence only)."""
    frame = _cp_frame_with(page, SUMMARY_DURATION, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("Multi-booking summary component did not render")

    actual_location = _text(frame, SUMMARY_LOCATION)
    assert location in actual_location, f"summary location {actual_location!r} missing {location!r}"
    actual_duration = _text(frame, SUMMARY_DURATION)
    assert duration in actual_duration, f"summary duration {actual_duration!r} missing {duration!r}"
    actual_staff = _text(frame, SUMMARY_STAFF)
    assert providing_staff in actual_staff, f"summary staff {actual_staff!r} missing {providing_staff!r}"

    # date/time = default in the legacy table -> assert they are present (non-empty).
    for selector, label in ((SUMMARY_START_DATE, "date"), (SUMMARY_START_TIME, "time")):
        value = _text(frame, selector)
        assert value, f"summary {label} was empty"


# --------------------------------------------------------------------------- #
# Intake form -> booking confirmation
# --------------------------------------------------------------------------- #
def fill_intake_and_confirm(page: Page, *, first_name: str, last_name: str, email: str) -> None:
    """Fill the scheduling intake form and confirm (legacy intakeForm.fillIntakeForm)."""
    frame = _cp_frame_with(page, INTAKE_FORM, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("Scheduling intake form did not appear")
    frame.locator(INTAKE_EMAIL).first.fill(email, timeout=UI_TIMEOUT)
    _fill_labeled(frame, "First Name", first_name)
    _fill_labeled(frame, "Last Name", last_name)
    confirm = frame.locator(INTAKE_CONFIRM).first
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click(timeout=UI_TIMEOUT)


def assert_booking_confirmation(page: Page, *, title: str) -> None:
    """Assert the booking confirmation page title (legacy bookingConfirmation.getBookingConfirmation)."""
    frame = _cp_frame_with(page, CONFIRM_CONTAINER, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("Booking confirmation page was not reached")
    actual = _text(frame, CONFIRM_TITLE)
    assert title in actual, f"booking confirmation {actual!r} missing {title!r}"


# --------------------------------------------------------------------------- #
# CP dashboard -> meeting page
# --------------------------------------------------------------------------- #
def open_meeting(page: Page, meeting_name: str):
    """Open the CP dashboard, the bookings list, and the meeting (legacy ClientPortalDashboard
    already-logged-in branch: switch into cp_iframe, click .business-title, open bookings,
    click the meeting row)."""
    frame = _cp_frame_with(page, V_APPLICATION, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("Client portal did not load after booking")
    dash = frame.locator(DASHBOARD_BTN).first
    dash.wait_for(state="visible", timeout=CP_TIMEOUT)
    dash.click(timeout=UI_TIMEOUT)

    frame = _cp_frame_with(page, BOOKINGS_MENU, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("Client-portal bookings menu did not appear after opening the dashboard")
    frame.locator(BOOKINGS_MENU).first.click(timeout=UI_TIMEOUT)

    item = _booking_item(page, meeting_name)
    if item is None:
        raise AssertionError(f"Booking {meeting_name!r} did not appear in the bookings list")
    item.click(timeout=UI_TIMEOUT)
    frame = _cp_frame_with(page, BOOKING_TITLE, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("Client-portal meeting page did not open")
    return frame


def assert_meeting(page: Page, *, meeting_name: str, meeting_state: str, linked_bookings: str) -> None:
    """Assert the CP meeting page name, state and linked bookings (legacy CPMeeting.getCPMeetingData
    + getMeetingRelatedBookings)."""
    frame = _cp_frame_with(page, BOOKING_TITLE, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("Client-portal meeting page did not render (no booking title)")
    actual_name = _text(frame, BOOKING_TITLE)
    assert meeting_name in actual_name, f"meeting name {actual_name!r} missing {meeting_name!r}"
    actual_state = _text(frame, MEETING_STATE)
    assert meeting_state in actual_state, f"meeting state {actual_state!r} missing {meeting_state!r}"

    titles = frame.locator(LINKED_BOOKING_TITLE)
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    linked_text = ""
    while time.monotonic() < deadline:
        count = titles.count()
        if count > 0:
            linked_text = " ".join(
                (titles.nth(i).inner_text(timeout=1_000) or "") for i in range(count)
            )
            if linked_bookings in linked_text:
                return
        time.sleep(SETTLE_MS / 1000)
    raise AssertionError(f"linked bookings {linked_text!r} missing {linked_bookings!r}")


# --------------------------------------------------------------------------- #
# Scheduler "next step is futureEvent"
# --------------------------------------------------------------------------- #
def assert_next_step_future_event(page: Page) -> None:
    """Assert the scheduler's next step is the future-event list (legacy
    CPScheduler.schedulerStepIs("futureEvent") -> .future-events-list)."""
    frame = _cp_frame_with(page, FUTURE_EVENT, timeout=CP_TIMEOUT)
    if frame is None:
        raise AssertionError("Scheduler did not advance to the future-event step")


# --------------------------------------------------------------------------- #
# Frame / element helpers (mirrors cp_scheduling_helpers)
# --------------------------------------------------------------------------- #
def _fill_labeled(frame, label: str, value: str) -> None:
    field = frame.locator(f'xpath=//label[contains(text(),"{label}")]/../input').first
    field.wait_for(state="visible", timeout=UI_TIMEOUT)
    field.fill(value, timeout=UI_TIMEOUT)


def _booking_item(page: Page, title: str, timeout: int = CP_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        frame = _cp_frame_with(page, BOOKING_TITLE, timeout=2_000)
        if frame is not None:
            items = frame.locator(BOOKING_TITLE)
            for index in range(items.count()):
                item = items.nth(index)
                try:
                    if title in (item.inner_text(timeout=1_000) or ""):
                        return item
                except Exception:  # noqa: BLE001 - re-render between reads
                    continue
        time.sleep(SETTLE_MS / 1000)
    return None


def _text(frame, selector: str) -> str:
    loc = frame.locator(selector).first
    loc.wait_for(state="visible", timeout=UI_TIMEOUT)
    return (loc.inner_text(timeout=UI_TIMEOUT) or "").strip()


def _cp_frame_with(page: Page, selector: str, timeout: int = CP_TIMEOUT):
    """Return the first frame containing ``selector`` (the client portal renders in cp_iframe,
    but the livesite shell sometimes nests it differently, so scan all frames)."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        named = page.frame(name="cp_iframe")
        candidates = [named] if named is not None else []
        candidates += [f for f in page.frames if f is not named]
        for frame in candidates:
            if frame is None:
                continue
            try:
                if frame.locator(selector).count() > 0:
                    return frame
            except Exception:  # noqa: BLE001 - frame may be navigating
                continue
        time.sleep(SETTLE_MS / 1000)
    return None
