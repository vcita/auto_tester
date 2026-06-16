"""UI + API helpers for the scheduling-events migration (VCITA2-14026).

Covers the legacy automation-js chain for tempo/scheduling-events.feature:
- back-office event scheduling (QuickActions/calendar "New" -> Group event), assigning
  a specific staff and the next-month date,
- reading the event-instance details (location/date/state/price/staff/registration
  availability/attendance summary/attendees),
- registering multiple clients via the Register Clients picker,
- reading the attendee state table (registered/unregistered, "Canceled by ...",
  paid/unpaid, per-category index),
- unregistering an attendee from the back office, and
- self-cancelling a registration from the client portal meeting page.

The event detail page renders in the Angular frontage iframe (``iframe[title="angularjs"]``)
with the attendee list nested in the Vue layout iframe (``#vue_iframe_layout``). Selectors
mirror the current frontage source and the legacy page objects (event.js, createMeetingDialog.js,
clientPortalMeeting.js); payment + CP-conversation flows reuse the event_payments helpers.
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page

from tests.account_api import account_request, get_business, pivot_uid
from tests.salsa.payments.event_payments.event_payments_helpers import (
    CP_IFRAME,
    CP_NAV_TIMEOUT,
    CP_VITRAGE,
)

UI_TIMEOUT = 5000
# Navigation / cross-iframe (POV->Angular->Vue) readiness legitimately exceeds the 5s
# element cap; documented bounded exception (mirrors event_payments_helpers).
PAGE_TIMEOUT = 10000
NAV_TIMEOUT = 10000
SETTLE_MS = 250


# --------------------------------------------------------------------------- #
# API helpers
# --------------------------------------------------------------------------- #
def find_event_uid(context: dict, service_name: str) -> str:
    """Resolve the most-recent event-instance uid for ``service_name`` via API.

    The back-office scheduling UI does not expose the uid, so the event page is opened
    by uid resolved from the event_instances list (mirrors legacy addBookingToContext
    polling get_events)."""
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    last: list = []
    while time.monotonic() < deadline:
        response = account_request(context, "GET", "/v2/event_instances")
        last = _extract_events(response)
        matches = [e for e in last
                   if isinstance(e, dict) and (e.get("title") or e.get("name")) == service_name]
        if matches:
            matches.sort(key=lambda e: e.get("created_at") or e.get("start_time") or "", reverse=True)
            return matches[0].get("uid") or matches[0].get("id")
        time.sleep(SETTLE_MS / 1000)
    raise AssertionError(
        f"No event instance titled {service_name!r} found via API "
        f"(got {[e.get('title') for e in last][:5]})"
    )


def _extract_events(response) -> list:
    """Normalize the GET /v2/event_instances response (top-level list or wrapped)."""
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        data = response.get("data")
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("event_instances") or []
        return response.get("event_instances") or []
    return []


def app_base(context: dict) -> str:
    base = (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return base


def _frames(page: Page):
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator("#vue_iframe_layout")
    return outer, inner


def open_event(page: Page, context: dict, event_uid: str):
    """Open the back-office event detail page and return (outer, inner) frame locators."""
    target = f"{app_base(context)}/app/events/{event_uid}"
    if f"/app/events/{event_uid}" not in page.url:
        page.goto(target, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        page.wait_for_url("**/app/events/**", timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
    page.wait_for_selector('iframe[title="angularjs"]', state="visible", timeout=PAGE_TIMEOUT)
    return _frames(page)


# --------------------------------------------------------------------------- #
# Back-office event scheduling (UI)
# --------------------------------------------------------------------------- #
def schedule_event_ui(page: Page, context: dict, service_name: str, staff_name: str) -> str:
    """Schedule an event from the back office for ``service_name`` next month (day 10),
    assigned to ``staff_name``. Returns the resolved event-instance uid.

    Mirrors legacy QuickActions.scheduleEvent -> CreateMeetingDialog.scheduleEvent. The
    booking dialog renders in a dedicated Vue iframe (separate from the calendar frame),
    so the dialog is driven through the frame that actually hosts the service select.
    """
    from tests.tempo.scheduling.appointments.appointment_helpers import open_calendar_page

    if "/app/calendar" not in page.url:
        open_calendar_page(page)

    _, inner = _frames(page)
    new_btn = inner.get_by_role("button", name="New")
    new_btn.wait_for(state="visible", timeout=PAGE_TIMEOUT)
    new_btn.click()
    group_event_option = inner.get_by_role("menuitem", name="Group event")
    group_event_option.wait_for(state="visible", timeout=UI_TIMEOUT)
    group_event_option.click()

    dialog = _dialog_frame(page)
    _select_service(dialog, service_name)
    _set_start_date_next_month_day10(dialog)
    _assign_staff(dialog, staff_name)

    submit = dialog.locator('[data-qa="dialog-submit-button"]:not([disabled]), '
                            'button:has-text("Create Event"):not([disabled])').first
    submit.wait_for(state="visible", timeout=NAV_TIMEOUT)
    submit.click()
    _wait_dialog_closed(page)

    return find_event_uid(context, service_name)


def _dialog_frame(page: Page):
    """Return the Vue frame hosting the open event dialog (identified by the service select)."""
    deadline = time.monotonic() + PAGE_TIMEOUT / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator('[data-qa="service-select-input"], [role="combobox"]').count() > 0:
                    return frame
            except Exception:  # noqa: BLE001 - frame may be navigating
                continue
        page.wait_for_timeout(SETTLE_MS)
    raise AssertionError("Event dialog frame (service select) did not appear")


def _select_service(dialog, service_name: str) -> None:
    combobox = dialog.locator('[data-qa="service-select-input"]').first
    if combobox.count() == 0:
        combobox = dialog.get_by_role("combobox").first
    combobox.wait_for(state="visible", timeout=NAV_TIMEOUT)
    combobox.click()
    dialog.get_by_role("listbox").first.wait_for(state="visible", timeout=UI_TIMEOUT)
    option = dialog.get_by_role("option").filter(has_text=service_name).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()


def _set_start_date_next_month_day10(dialog) -> None:
    start_date = dialog.locator('[data-qa="date-picker-text-input"]').first
    start_date.wait_for(state="visible", timeout=NAV_TIMEOUT)
    start_date.click()
    menu = dialog.locator(".date-picker-menu-content, .v-date-picker-header").first
    menu.wait_for(state="visible", timeout=UI_TIMEOUT)
    # v-date-picker header buttons: [prev, next]; .last = next month.
    dialog.locator(".v-date-picker-header button").last.click()
    day_btn = dialog.locator(".v-date-picker-table button:visible").filter(
        has_text=re.compile(r"^\s*10\s*$")
    )
    day_btn.last.wait_for(state="visible", timeout=UI_TIMEOUT)
    day_btn.last.click()


def _assign_staff(dialog, staff_name: str) -> None:
    """Assign ``staff_name`` in the event dialog staff selection.

    The dialog exposes a staff combobox (legacy ``.staff-selection``); pick the option
    by display name. Best-effort across the current combobox markup."""
    staff_select = dialog.locator('.staff-selection, [data-qa="staff-select-input"]').first
    if staff_select.count() == 0:
        # Fall back to the last combobox (service is the first), if present.
        comboboxes = dialog.get_by_role("combobox")
        if comboboxes.count() < 2:
            return  # No staff selector in this dialog variant; keep default owner.
        staff_select = comboboxes.last
    staff_select.wait_for(state="visible", timeout=UI_TIMEOUT)
    staff_select.click()
    option = dialog.get_by_role("option").filter(has_text=staff_name).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()


def _wait_dialog_closed(page: Page) -> None:
    deadline = time.monotonic() + PAGE_TIMEOUT / 1000
    while time.monotonic() < deadline:
        still_open = False
        for frame in page.frames:
            try:
                if frame.locator('[data-qa="dialog-submit-button"]').count() > 0:
                    still_open = True
                    break
            except Exception:  # noqa: BLE001
                continue
        if not still_open:
            return
        page.wait_for_timeout(SETTLE_MS)


# --------------------------------------------------------------------------- #
# Event details (read)
# --------------------------------------------------------------------------- #
SUMMARY_NAME = "div.summary-header h3"
SUMMARY_DATE = "div.summary-header h2"
EVENT_LOCATION = '[data-qa="booking-where"]'
EVENT_STATE = "div.entity-summary-row span.capitalize.bold"
ATTENDANCE_SUMMARY = ".attendance-summary-row"
MORE_DETAILS_SPAN = ".more-details span"


def read_event_details(page: Page, context: dict, event_uid: str) -> dict:
    """Read the back-office event detail fields (mirrors legacy Event.getEventData).

    Returns name/location/state/attendance_summary/price/registration_availability/
    assigned_staff plus the attendees name list."""
    outer, inner = _frames(page)
    open_event(page, context, event_uid)
    outer.locator(SUMMARY_NAME).first.wait_for(state="visible", timeout=NAV_TIMEOUT)

    more = outer.locator(MORE_DETAILS_SPAN)
    more_texts = [t.strip() for t in more.all_inner_texts()] if more.count() else []

    return {
        "event_name": _text(outer, SUMMARY_NAME),
        "event_date_text": _text(outer, SUMMARY_DATE),
        "event_location": _text(outer, EVENT_LOCATION),
        "event_state": _text(outer, EVENT_STATE).upper(),
        "attendance_summary": " ".join(_text(outer, ATTENDANCE_SUMMARY).split()),
        "more_details": more_texts,
        "attendees_info": read_attendee_names(inner),
    }


def read_attendee_names(inner) -> list[str]:
    names = inner.locator(".attendance-list .attendance-item .matter-name")
    if names.count() == 0:
        return []
    return [t.strip() for t in names.all_inner_texts() if t.strip()]


# --------------------------------------------------------------------------- #
# Register clients (UI)
# --------------------------------------------------------------------------- #
def _wait_attendees_ui(page: Page, expected: int) -> bool:
    """Poll the back-office attendee list until at least ``expected`` names render.

    The Register-Clients round-trip updates the attendees panel reactively; gating on
    it (rather than a fixed sleep) verifies the registration actually completed."""
    _, inner = _frames(page)
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if len(read_attendee_names(inner)) >= expected:
            return True
        time.sleep(SETTLE_MS / 1000)
    return False


def _dump_buttons(page: Page, label: str) -> None:
    """Print visible button labels across all frames (registration debugging aid)."""
    for frame in page.frames:
        try:
            labels = frame.eval_on_selector_all(
                "button",
                "els => els.filter(e => e.offsetParent !== null && (e.textContent||'').trim())"
                ".map(e => (e.textContent||'').trim().slice(0, 40)).slice(0, 40)",
            )
        except Exception:  # noqa: BLE001 - detached/cross-origin frame
            continue
        if labels:
            print(f"  [DIAG {label} buttons @ {frame.url[:60]}] {labels}")


def register_clients_ui(page: Page, context: dict, event_uid: str, client_names: list[str]) -> None:
    """Register the given clients to the event via the Register Clients picker.

    Mirrors legacy Event.registerClient -> ClientPickerDialog.selectClients: open the
    picker, search + select each client, continue, and confirm the registration."""
    outer, _ = _frames(page)
    open_event(page, context, event_uid)

    register_btn = outer.get_by_role("button", name="Register Clients")
    register_btn.wait_for(state="visible", timeout=NAV_TIMEOUT)
    register_btn.click()
    dialog = outer.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=NAV_TIMEOUT)

    for name in client_names:
        # Re-locate the search input each iteration (its accessible name changes once a
        # chip is added) and clear it with the keyboard before typing the next client.
        search = dialog.get_by_role("textbox").first
        search.wait_for(state="visible", timeout=UI_TIMEOUT)
        search.click(timeout=UI_TIMEOUT)
        search.press("Meta+A")
        search.press("Backspace")
        search.press_sequentially(name, delay=30)
        # The list filters to this client; its chip only exists after selection, so the
        # first text match in the filtered list is the row to click.
        row = dialog.get_by_text(name, exact=False).first
        row.wait_for(state="visible", timeout=NAV_TIMEOUT)
        row.click(timeout=UI_TIMEOUT)

    continue_btn = outer.get_by_role("button", name="Continue")
    continue_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    continue_btn.click(timeout=UI_TIMEOUT)

    # Continue advances the picker to a confirmation step (Send / Cancel) that completes the
    # registration. Scope to the dialog so we don't match the page's "Register Clients" button.
    dialog = outer.get_by_role("dialog").last
    confirm = dialog.get_by_role(
        "button", name=re.compile(r"^(Send|Confirm|Register clients)$", re.I)
    ).last
    confirm.wait_for(state="visible", timeout=NAV_TIMEOUT)
    confirm.evaluate("el => el.click()")

    # Gate on the attendee list actually populating, so the UI assertion that follows is
    # not racing the registration round-trip (and so a no-op confirm surfaces here).
    if not _wait_attendees_ui(page, expected=len(client_names)):
        _dump_buttons(page, "REGISTER")
        raise AssertionError(
            f"Registration did not add {len(client_names)} attendees for {event_uid}")
    register_btn.wait_for(state="visible", timeout=NAV_TIMEOUT)


# --------------------------------------------------------------------------- #
# Attendee state table (read) - scenarios 2/2B
# --------------------------------------------------------------------------- #
UNPAID_LIST = ".solo-attendees-list"
PAID_LIST = ".attendees-list"
ATTENDEE_ITEM = ".attendance-item"
ATTENDEE_NAME = ".matter-name"
CANCEL_DESC = ".status-desc"


EVENT_LIST_MENU = '[data-qa="VcMenuItem-calendar-subitem-event_list"]'
CALENDAR_MENU = '[data-qa="VcMenuItem-calendar"]'


def refresh_event_view(page: Page) -> None:
    """Navigate to Event List (real menu click) so the next ``open_event`` re-fetches the
    detail. Needed to observe out-of-band changes (e.g. a client-portal self-cancel made in
    a separate session) that the still-open back-office page does not live-update."""
    item = page.locator(EVENT_LIST_MENU).first
    try:
        item.wait_for(state="visible", timeout=UI_TIMEOUT)
    except Exception:  # noqa: BLE001 - Calendar submenu collapsed; expand it first
        parent = page.locator(CALENDAR_MENU).first
        parent.wait_for(state="visible", timeout=PAGE_TIMEOUT)
        parent.click()
        item.wait_for(state="visible", timeout=PAGE_TIMEOUT)
    item.click()
    page.wait_for_url("**/app/event-list**", timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")


def read_attendees(page: Page, context: dict, event_uid: str,
                   refresh: bool = False) -> list[dict]:
    """Read the attendee state table: name/state/comment/payment_status/index_per_category.

    Unpaid attendees render in ``.solo-attendees-list``, paid in ``.attendees-list``;
    ``index_per_category`` is the 1-based position within each list (mirrors legacy
    getAttendeesData). ``refresh`` re-navigates via Event List first so out-of-band changes
    (client-portal self-cancel) are picked up."""
    if refresh:
        refresh_event_view(page)
    _, inner = _frames(page)
    open_event(page, context, event_uid)
    inner.locator(ATTENDEE_NAME).first.wait_for(state="visible", timeout=NAV_TIMEOUT)

    result: list[dict] = []
    for payment_status, container in (("unpaid", UNPAID_LIST), ("paid", PAID_LIST)):
        items = inner.locator(f"{container} {ATTENDEE_ITEM}")
        for i in range(items.count()):
            item = items.nth(i)
            name = (item.locator(ATTENDEE_NAME).first.inner_text() or "").strip()
            if not name:
                continue
            desc_loc = item.locator(CANCEL_DESC)
            comment = (desc_loc.first.inner_text().strip() if desc_loc.count() else "")
            result.append({
                "name": name,
                "payment_status": payment_status,
                "state": "unregistered" if comment else "registered",
                "comment": comment,
                "index_per_category": i + 1,
            })
    return result


def attendees_counter(page: Page, context: dict, event_uid: str) -> int:
    """Read the attendees-tab counter (mirrors legacy getAttendeesCounter)."""
    _, inner = _frames(page)
    open_event(page, context, event_uid)
    tab = inner.locator("[tab='attendees'], [role='tab']").filter(
        has_text=re.compile(r"Attendees", re.I)
    ).first
    tab.wait_for(state="visible", timeout=NAV_TIMEOUT)
    match = re.search(r"\d+", tab.inner_text() or "")
    return int(match.group()) if match else 0


def find_attendee(attendees: list[dict], name: str) -> dict:
    """Return the attendee row whose name matches ``name`` (case/space-insensitive)."""
    norm = re.sub(r"\s+", " ", name).strip().lower()
    for attendee in attendees:
        if re.sub(r"\s+", " ", attendee["name"]).strip().lower() == norm:
            return attendee
    raise AssertionError(f"Attendee {name!r} not found in {[a['name'] for a in attendees]}")


# --------------------------------------------------------------------------- #
# Back-office attendee payment (online record / POS) - scenarios 2/2B
# --------------------------------------------------------------------------- #
def _open_attendee_payment_status(page: Page, context: dict, event_uid: str,
                                  client_name: str):
    """Open an attendee's booking payment-status detail from the event page.

    Mirrors legacy Event.goToEventAttendancePaymentRequest: in the Vue attendee list,
    open the attendee's actions menu and choose "Go to payment status"."""
    outer, inner = _frames(page)
    open_event(page, context, event_uid)
    container = inner.locator(f'[data-qa="{client_name}"]').first
    container.wait_for(state="visible", timeout=NAV_TIMEOUT)
    container.hover()
    activator = container.locator("button.activator-container, button.three-dots").first
    activator.wait_for(state="visible", timeout=UI_TIMEOUT)
    activator.evaluate("el => el.click()")
    goto_ps = inner.locator('[data-qa="gotoPaymentStatus"]')
    if goto_ps.count() == 0:
        goto_ps = outer.locator('[data-qa="gotoPaymentStatus"]')
    goto_ps.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    goto_ps.first.click()


def pay_for_attendee_bo(page: Page, context: dict, event_uid: str, client_name: str,
                        amount: str, pos: bool = False) -> None:
    """Pay an attendee's event payment request from the back office (mirrors legacy
    Event.payForEvent -> BookingPaymentRequestPage.payForMeeting).

    ``pos=False`` records the payment through the take-payment record dialog; ``pos=True``
    routes through Point of Sale (record a Cash sale). Reuses the event_payments helpers
    so the payment-status / POS selectors stay in one place."""
    from tests.salsa.payments.event_payments.event_payments_helpers import (
        TAKE_PAYMENT_BTN, TAKE_PAYMENT_CONFIRM, POS_CHECKOUT_ACTIVATOR,
        POS_CHECKOUT_RECORD, POS_TAKE_PAYMENT_DIALOG, POS_METHOD_SELECT,
        POS_METHOD_OPTION, _payment_status_frame, _take_payment_record,
    )
    _open_attendee_payment_status(page, context, event_uid, client_name)
    frame = _payment_status_frame(page)
    if not pos:
        _take_payment_record(frame, amount)
        _wait_payment_paid(frame)
        return

    from tests.salsa.payments.deposits.deposits_invoice_ui import (
        FAST_UI_TIMEOUT, LOAD_TIMEOUT, _find_control, _require,
    )
    frame.locator(TAKE_PAYMENT_BTN).first.click()
    _require(page, POS_CHECKOUT_ACTIVATOR, "POS checkout activator",
             timeout=LOAD_TIMEOUT).click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_CHECKOUT_RECORD, "POS record-payment action").click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_TAKE_PAYMENT_DIALOG, "Take payment dialog", timeout=LOAD_TIMEOUT)
    _require(page, POS_METHOD_SELECT, "Record method picker").click(timeout=FAST_UI_TIMEOUT)
    _require(page, POS_METHOD_OPTION, "Cash record option").click(timeout=FAST_UI_TIMEOUT)
    _require(page, TAKE_PAYMENT_CONFIRM, "Take payment confirm").click(timeout=FAST_UI_TIMEOUT)
    deadline = time.monotonic() + LOAD_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if _find_control(page, POS_TAKE_PAYMENT_DIALOG, timeout=300) is None:
            break
        time.sleep(0.2)
    else:
        raise AssertionError("Take payment dialog did not close after recording the POS sale")
    _wait_payment_paid(_payment_status_frame(page))


def _wait_payment_paid(frame) -> None:
    """Poll the booking payment-status until it reads PAID (records are eventually
    consistent); gates the attendee-table read so it does not race the rollup."""
    from tests.salsa.payments.event_payments.event_payments_helpers import PS_STATE
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    last = ""
    while time.monotonic() < deadline:
        try:
            last = frame.locator(PS_STATE).first.inner_text(timeout=2000)
        except Exception:  # noqa: BLE001 - frame re-render during rollup
            last = ""
        if "PAID" in last.upper():
            return
        time.sleep(SETTLE_MS / 1000)
    raise AssertionError(f"Payment did not reach PAID (last status {last!r})")


def cancelled_by_business_text(context: dict) -> str:
    """The BO-unregister comment is 'Canceled by {staff}', where {staff} resolves to the
    business/account name (legacy auto_account.name)."""
    business = get_business(context)
    name = business.get("name") or business.get("business_name") or ""
    return f"Canceled by {name}".strip()


# --------------------------------------------------------------------------- #
# Back-office unregister
# --------------------------------------------------------------------------- #
def unregister_attendee_bo(page: Page, context: dict, event_uid: str, client_name: str) -> None:
    """Unregister an attendee from the back office (mirrors legacy Event.unregisterClient).

    Hover the attendee, open the three-dots menu, choose Cancel registration, confirm.

    The attendee menu lives in the Vue iframe, but the confirm dialog (Message + Submit)
    is a page-level Angular modal - so it is confirmed through the outer frame."""
    outer, inner = _frames(page)
    open_event(page, context, event_uid)
    attendee = inner.get_by_text(client_name).first
    attendee.wait_for(state="visible", timeout=NAV_TIMEOUT)
    attendee.hover()

    container = attendee.locator('xpath=ancestor::*[contains(@class,"attendance-item")][1]')
    if container.count() == 0:
        container = attendee.locator("xpath=ancestor::*[position()=2]")
    menu_btn = container.locator("button.three-dots, button.activator-container").first
    menu_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    menu_btn.evaluate("el => { el.scrollIntoView({block:'center'}); el.click(); }")

    cancel_option = inner.get_by_text("Cancel registration").first
    cancel_option.wait_for(state="visible", timeout=UI_TIMEOUT)
    cancel_option.click()

    submit = outer.locator(
        'button[ng-click="cancelEventAttendance()"]').or_(
        outer.get_by_role("button", name="Submit")).first
    submit.wait_for(state="visible", timeout=NAV_TIMEOUT)
    submit.click()
    submit.wait_for(state="hidden", timeout=NAV_TIMEOUT)

    # The attendee list re-renders and re-orders the cancelled attendee, so gate on the
    # cancelled state actually showing before returning (reading too early races it).
    deadline = time.monotonic() + NAV_TIMEOUT / 1000
    row = inner.locator(".attendance-item").filter(has_text=client_name).first
    while time.monotonic() < deadline:
        desc = row.locator(".status-desc")
        if desc.count() > 0 and (desc.first.inner_text() or "").strip():
            return
        time.sleep(SETTLE_MS / 1000)


# --------------------------------------------------------------------------- #
# Client-portal self-cancel
# --------------------------------------------------------------------------- #
CP_BOOKINGS_MENU = "[data-qa='client-area-menu-bookings']"
CP_BOOKING_ITEM = ".booking-list-item.list-item"
CP_BOOKING_TITLE = ".booking-title"
CP_BOOKING_PAGE = ".booking-page"


def _open_cp_bookings(cp_page, cp_frame, cp_url: str):
    """Open the client portal and return the visible Bookings menu locator.

    The CP first paint inside the Vitrage iframe is the slowest, most network-dependent
    step in the flow and occasionally renders blank past the 15s cap. Reload once (rather
    than a single long wait) so a slow cold load doesn't fail the whole scenario."""
    bookings = cp_frame.locator(CP_BOOKINGS_MENU).first
    for attempt in range(2):
        try:
            cp_page.goto(cp_url, wait_until="domcontentloaded", timeout=CP_NAV_TIMEOUT)
            bookings.wait_for(state="visible", timeout=CP_NAV_TIMEOUT)
            return bookings
        except Exception:  # noqa: BLE001 - slow/blank CP cold load; retry once with a reload
            if attempt == 1:
                raise
    return bookings


def cp_self_cancel_meeting(page: Page, context: dict, token: str, meeting_name: str,
                           message: str = "") -> None:
    """Open the client portal as the client and cancel their own event registration.

    Mirrors legacy CPScheduler: open the CP via client_jwt, bookings list -> meeting ->
    Cancel action -> confirm dialog (message optional). Runs in a fresh browser context
    (same pattern as assert_cp_conversation_title) so the back-office session is intact.
    """
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    try:
        cp_page = cp_context.new_page()
        cp_url = f"{CP_VITRAGE}/site/{pivot_uid(context)}/action?client_jwt={token}"
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        bookings = _open_cp_bookings(cp_page, cp_frame, cp_url)
        bookings.click()

        meeting = cp_frame.locator(CP_BOOKING_ITEM).filter(has_text=meeting_name).first
        meeting.wait_for(state="visible", timeout=CP_NAV_TIMEOUT)
        meeting.click()
        cp_frame.locator(CP_BOOKING_PAGE).first.wait_for(state="visible", timeout=CP_NAV_TIMEOUT)

        cancel = cp_frame.locator(".action.v-btn").filter(has_text=re.compile(r"Cancel", re.I)).first
        cancel.wait_for(state="visible", timeout=CP_NAV_TIMEOUT)
        cancel.click()

        dialog = cp_frame.locator(".v-dialog__content--active").first
        dialog.wait_for(state="visible", timeout=CP_NAV_TIMEOUT)
        if message:
            dialog.locator("textarea").first.fill(message)
        submit = dialog.locator("button.action-btn.submit-btn, button.submit-btn").first
        submit.wait_for(state="visible", timeout=UI_TIMEOUT)
        submit.click()
        dialog.wait_for(state="hidden", timeout=CP_NAV_TIMEOUT)
        # Confirm the cancellation persisted before the back office re-reads it: wait for the
        # CP success state ("Your booking is cancelled" / Cancelled badge) rather than a fixed
        # sleep, so the out-of-band cancel has propagated server-side.
        cp_frame.get_by_text(re.compile(r"cancell?ed", re.I)).first.wait_for(
            state="visible", timeout=CP_NAV_TIMEOUT)
    finally:
        cp_context.close()


def assert_cp_conversation_title(page: Page, context: dict, token: str, title: str) -> None:
    """Open the client portal as the client (by ``token``) and assert a conversation
    bubble header includes ``title`` (mirrors legacy 'conversation ... includes title').

    Token-parameterized variant of the event_payments helper so any seeded client can be
    checked; runs in a fresh browser context to keep the back-office session intact."""
    cp_context = page.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, locale="en-US", timezone_id="America/New_York"
    )
    try:
        cp_page = cp_context.new_page()
        cp_page.goto(f"{CP_VITRAGE}/site/{pivot_uid(context)}/action?client_jwt={token}",
                     wait_until="domcontentloaded", timeout=CP_NAV_TIMEOUT)
        cp_frame = cp_page.frame_locator(CP_IFRAME)
        chat = cp_frame.locator('[data-qa="headerChatBtn"]').first
        chat.wait_for(state="visible", timeout=CP_NAV_TIMEOUT)
        chat.click()
        header = cp_frame.locator('[data-qa="bubble-header"]').filter(has_text=title).first
        header.wait_for(state="visible", timeout=CP_NAV_TIMEOUT)
    finally:
        cp_context.close()


def _text(frame_or_locator, selector: str) -> str:
    loc = frame_or_locator.locator(selector).first
    loc.wait_for(state="visible", timeout=UI_TIMEOUT)
    return (loc.inner_text(timeout=UI_TIMEOUT) or "").strip()
