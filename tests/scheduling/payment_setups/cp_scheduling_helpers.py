"""Client-portal scheduler helpers for the CP-scheduling-with-taxes scenario (VCITA2-14008).

Covers the legacy chain ServicesSettings.grabLink -> CPScheduler.bookingFromCP ->
ClientPortalDashboard/CPMeeting:
- grab a service's public link from the business services list (Angular row 3-dot menu ->
  "Copy public link" -> Vue ``vc-input-modal`` -> ``.link-container__link``),
- open it anonymously (public livesite embeds the client portal in the ``cp_iframe``),
- assert the scheduler calendar booking summary (service / +Tax / price),
- book through the calendar + intake form, then
- navigate to the meeting page in the (same-session) client portal and assert the meeting.

Selectors mirror the current legacy page objects (calendar.js, intakeForm.js,
bookingConfirmation.js, dashboard.js, bookingList.js, clientPortalMeeting.js).
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

from tests.payments.offset_fees.offset_fees_checkout import vitrage_base

UI_TIMEOUT = 10_000
SETTLE_MS = 250

# Business services list (Angular frontage frame) + Vue copy-link modal.
SERVICES_PATH = "/app/settings/services"
SERVICE_ROW = "div.list-item:not(.main-actions)"
SERVICE_TITLE = ".titles .title"
COPY_LINK_OPTION = "Copy public link"

# Client-portal scheduler (cp_iframe).
CALENDAR_CONTAINER = '[data-qa="ScheduleSelection"] .schedule-container'
SUMMARY_SERVICE = ".service-section"
SUMMARY_TAX = ".tax"
SUMMARY_PRICE = ".service-summary-container .price"
TIME_SLOT = "button.time-slot"
CONTINUE_BTN = ".submit-button span, .summary-card__cta"
INTAKE_FORM = '.scheduling-intake-form[data-qa="SchedulingIntakeForm"]'
INTAKE_EMAIL = 'input[type="email"]'
CONFIRM_BOOKING = '[data-qa="ConfirmBooking"]'

# Client-portal dashboard + meeting page.
DASHBOARD_BTN = ".business-title"
BOOKINGS_MENU = "[data-qa='client-area-menu-bookings']"
BOOKING_LIST_ITEM = ".booking-list-item.list-item"
BOOKING_TITLE = ".booking-title"
BOOKING_PAGE = ".booking-page"
MEETING_PRICE = ".booking-detail .price"
MEETING_TAX = ".tax"


def grab_service_link(page: Page, service_name: str) -> str:
    """Open the service row 3-dot menu, choose "Copy public link", and return the link URL."""
    base = page.url.split("/app/")[0]
    page.goto(f"{base}{SERVICES_PATH}", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    ng = page.frame_locator('iframe[title="angularjs"]')
    ng.get_by_role("heading", name="Settings / Services").wait_for(state="visible", timeout=UI_TIMEOUT)

    row = ng.locator(SERVICE_ROW).filter(has=ng.locator(SERVICE_TITLE, has_text=service_name)).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    row.hover()
    row.locator(".actions md-menu button").first.click(timeout=UI_TIMEOUT)
    ng.get_by_role("menuitem", name=COPY_LINK_OPTION).click(timeout=UI_TIMEOUT)

    # The "Copy link to share publicly" dialog can mount at any nesting level (POV / Angular /
    # Vuetage), so scan every frame for the http link. It may be rendered as text (a span/div)
    # or as a readonly input value (Vue keeps the URL as the value property), so check both.
    deadline = time.monotonic() + UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            url = _http_link_in_frame(frame)
            if url:
                return url
        time.sleep(SETTLE_MS / 1000)
    raise AssertionError("Copy-link dialog did not expose an http link in any frame")


def _http_link_in_frame(frame) -> str | None:
    """Return an http link rendered in ``frame`` (text element or readonly input value)."""
    try:
        for selector in (".link-container__link", "[data-qa='vc-input-modal'] input", "input"):
            loc = frame.locator(selector)
            for index in range(min(loc.count(), 4)):
                el = loc.nth(index)
                text = (el.input_value(timeout=400) if selector.endswith("input") else el.inner_text(timeout=400)) or ""
                text = text.strip()
                if text.startswith("http"):
                    return text
    except Exception:  # noqa: BLE001 - frame may be navigating / element detached
        return None
    return None


def open_scheduler(page: Page, link: str):
    """Navigate to the grabbed public link and return the scheduler's cp_iframe frame."""
    page.goto(link, wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    frame = _cp_frame_with(page, CALENDAR_CONTAINER)
    if frame is None:
        raise AssertionError("Client-portal scheduler calendar did not load from the grabbed link")
    return frame


def assert_calendar_summary(page: Page, *, service_name: str, tax: str, price: str) -> None:
    """Assert the scheduler calendar booking-summary shows the service, tax and price."""
    frame = _cp_frame_with(page, SUMMARY_SERVICE)
    if frame is None:
        raise AssertionError("Scheduler booking summary did not render")
    actual_service = _text(frame, SUMMARY_SERVICE)
    assert service_name in actual_service, f"summary service {actual_service!r} missing {service_name!r}"
    actual_tax = _text(frame, SUMMARY_TAX)
    assert tax in actual_tax, f"summary tax {actual_tax!r} missing {tax!r}"
    actual_price = _text(frame, SUMMARY_PRICE)
    assert price in actual_price, f"summary price {actual_price!r} missing {price!r}"


def book_appointment(page: Page, *, first_name: str, email: str) -> None:
    """Pick the default timeslot, continue to the intake form, fill it, and confirm."""
    frame = _cp_frame_with(page, TIME_SLOT)
    if frame is None:
        raise AssertionError("No timeslot was offered by the scheduler")
    frame.locator(TIME_SLOT).first.click(timeout=UI_TIMEOUT)
    _click_continue(page)

    frame = _cp_frame_with(page, INTAKE_FORM)
    if frame is None:
        raise AssertionError("Scheduling intake form did not appear")
    frame.locator(INTAKE_EMAIL).first.fill(email, timeout=UI_TIMEOUT)
    _fill_labeled(frame, "First Name", first_name)
    _click_continue(page)

    if _cp_frame_with(page, CONFIRM_BOOKING) is None:
        raise AssertionError("Booking confirmation page was not reached")


def open_meeting(page: Page, meeting_name: str):
    """From the post-booking session, open the dashboard, the bookings list, and the meeting."""
    frame = _cp_frame_with(page, DASHBOARD_BTN)
    if frame is None:
        raise AssertionError("Client-portal dashboard button was not available after booking")
    frame.locator(DASHBOARD_BTN).first.click(timeout=UI_TIMEOUT)

    frame = _cp_frame_with(page, BOOKINGS_MENU)
    if frame is None:
        raise AssertionError("Client-portal bookings menu did not appear after opening the dashboard")
    frame.locator(BOOKINGS_MENU).first.click(timeout=UI_TIMEOUT)

    item = _booking_item(page, meeting_name)
    if item is None:
        raise AssertionError(f"Booking {meeting_name!r} did not appear in the bookings list")
    item.click(timeout=UI_TIMEOUT)
    frame = _cp_frame_with(page, BOOKING_PAGE)
    if frame is None:
        raise AssertionError("Client-portal meeting page did not open")
    return frame


def assert_meeting(page: Page, *, meeting_name: str, price: str, tax: str) -> None:
    """Assert the client-portal meeting page shows the name, formatted price and tax.

    ``price`` is the rendered, currency-formatted value (e.g. ``$100.00``); the legacy
    ``m_currency=USD`` table value is the formatter input, not literal on-page text.
    """
    frame = _cp_frame_with(page, BOOKING_TITLE)
    if frame is None:
        raise AssertionError("Client-portal meeting page did not render (no booking title)")
    actual_name = _text(frame, BOOKING_TITLE)
    assert meeting_name in actual_name, f"meeting name {actual_name!r} missing {meeting_name!r}"
    actual_price = _text(frame, MEETING_PRICE)
    assert price in actual_price, f"meeting price {actual_price!r} missing {price!r}"
    actual_tax = _text(frame, MEETING_TAX)
    assert tax in actual_tax, f"meeting tax {actual_tax!r} missing {tax!r}"


def _click_continue(page: Page) -> None:
    frame = _cp_frame_with(page, CONTINUE_BTN)
    if frame is None:
        raise AssertionError("Continue/confirm button did not appear")
    frame.locator(CONTINUE_BTN).first.click(timeout=UI_TIMEOUT)


def _fill_labeled(frame, label: str, value: str) -> None:
    field = frame.locator(f'xpath=//label[contains(text(),"{label}")]/../input').first
    field.wait_for(state="visible", timeout=UI_TIMEOUT)
    field.fill(value, timeout=UI_TIMEOUT)


def _booking_item(page: Page, title: str, timeout: int = UI_TIMEOUT):
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        frame = _cp_frame_with(page, BOOKING_LIST_ITEM, timeout=2_000)
        if frame is not None:
            items = frame.locator(BOOKING_LIST_ITEM)
            for index in range(items.count()):
                item = items.nth(index)
                try:
                    if title in (item.locator(BOOKING_TITLE).first.inner_text(timeout=1_000) or ""):
                        return item
                except Exception:  # noqa: BLE001 - re-render between reads
                    continue
        page.wait_for_timeout(SETTLE_MS)
    return None


def _text(frame, selector: str) -> str:
    loc = frame.locator(selector).first
    loc.wait_for(state="visible", timeout=UI_TIMEOUT)
    return (loc.inner_text(timeout=UI_TIMEOUT) or "").strip()


def _cp_frame_with(page: Page, selector: str, timeout: int = UI_TIMEOUT):
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
