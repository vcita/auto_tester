"""UI helpers for the schedule_appointments migration (VCITA2-14025).

Builds on the proven multistaff appointment-dialog primitives (nested Angular->Vue iframe,
client/service pickers, future-date navigation, appointment read-back) and adds what the
scheduling-appointments.feature scenarios need that multistaff did not exercise:

- arbitrary meeting dates (previous_month / next_month / next_week, not just "future"),
- explicit start AND end times + the all-day toggle,
- request-client-confirmation, inline new client, assigned staff, additional recipients,
  and arrival windows,
- reschedule (outer-iframe Kendo datetime dialog) and cancel from the detail page,
- meeting-state / date / time / arrival-window verification (legacy appointment.js getMeetingData).
"""

from __future__ import annotations

import re
import time
from datetime import date, datetime, timedelta

from playwright.sync_api import Page

from tests.tempo.scheduling.appointments.appointment_helpers import UI_TIMEOUT, open_calendar_page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.tempo.scheduling.appointments.multistaff.multistaff_helpers import (
    _SETTLE_MS,
    _app_base,
    _dismiss_open_dialog,
    _fill_address_if_present,
    _pick_service,
    _schedule_button,
    _wait_for_new_appointment,
    meeting_text,
)
from tests.tempo.scheduling.appointments.schedule_appointments.schedule_appointments_api import (
    list_appointment_ids,
)


def _frames(page: Page):
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator("#vue_iframe_layout")
    return outer, inner


def resolve_meeting_date(name: str) -> date:
    """Translate a legacy date keyword to a concrete date (mirrors createMeetingDialog).

    Month keywords land on day 10 (legacy `nthOfMonth(10)`); week/day keywords offset today.
    """
    today = date.today()
    if name in ("previous_month", "next_month"):
        direction = -1 if name == "previous_month" else 1
        month_index = today.month - 1 + direction
        year = today.year + month_index // 12
        month = month_index % 12 + 1
        return date(year, month, 10)
    offsets = {"next_week": 7, "last_week": -7, "next_day": 1, "last_day": -1}
    if name in offsets:
        return today + timedelta(days=offsets[name])
    raise ValueError(f"Unsupported meeting_date keyword: {name!r}")


def schedule_appointment(
    page: Page,
    context: dict,
    *,
    service_name: str,
    client_name: str | None = None,
    new_client: dict | None = None,
    assigned_staff: str | None = None,
    meeting_date: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    all_day: bool = False,
    client_confirmation: bool = False,
    additional_recipients: str | None = None,
    arrival_window: str | None = None,
) -> str:
    """Schedule an appointment from the BO calendar dialog and return the new appointment id.

    Selects an existing client (``client_name``) or creates one inline (``new_client``) and
    optionally assigns a staff (``assigned_staff``). Date/time/all-day/confirmation/recipients/
    arrival-window mirror the legacy dialog.
    """
    before_ids = list_appointment_ids(context)
    open_calendar_page(page)
    outer, inner = _frames(page)

    _open_appointment_dialog(page, outer, inner, client_name=client_name, new_client=new_client)
    _pick_service(page, inner, service_name)
    _schedule_button(inner).wait_for(state="visible", timeout=UI_TIMEOUT)

    if assigned_staff:
        _select_assigned_staff(page, inner, assigned_staff)
    if additional_recipients:
        _add_additional_recipients(page, inner, additional_recipients)
    if arrival_window:
        _add_arrival_window(page, inner, arrival_window)
    if meeting_date:
        _select_calendar_date(page, inner, resolve_meeting_date(meeting_date))
    if all_day:
        _toggle_all_day(page, inner)
    if start_time:
        _select_time(inner, "start", start_time)
    if end_time:
        _select_time(inner, "end", end_time)
    _fill_address_if_present(page, inner)
    if client_confirmation:
        _enable_client_confirmation(inner)

    _submit_appointment(page, inner)
    return _wait_for_new_appointment(page, context, before_ids)


def _submit_appointment(page: Page, inner) -> None:
    """Click the Schedule-appointment button once it is enabled, retrying if the dialog stays open.

    Selecting staff/date/time triggers an async availability re-validation that briefly *disables*
    the book button; a click (even forced) while disabled silently no-ops and the appointment is
    never created. So wait until the button is enabled before clicking, then confirm the dialog
    closed (button hidden) — if it did not, the click landed during a transient disable, so retry
    once (legacy `_waitForParamsToLoadInDialog` similarly waits for the not-disabled button).
    """
    submit = _schedule_button(inner)
    submit.wait_for(state="visible", timeout=UI_TIMEOUT)
    for _ in range(2):
        if not submit.is_visible():
            return  # dialog already closed -> the (previous) click booked it; never re-submit
        _click_when_enabled(page, submit)
        try:
            submit.wait_for(state="hidden", timeout=UI_TIMEOUT)
            return
        except PlaywrightTimeoutError:
            continue
    # Dialog never closed; the booking read-back (_wait_for_new_appointment) reports the precise failure.


def _click_when_enabled(page: Page, locator) -> None:
    """Click ``locator`` only after it reports enabled.

    Vuetify/Angular dialog footers re-validate asynchronously and briefly set ``disabled`` on their
    confirm button; a click during that window silently no-ops (or, for `click()`, blocks on
    actionability until the timeout). Polling ``is_enabled`` first avoids both failure modes.
    """
    for _ in range(int(UI_TIMEOUT / _SETTLE_MS)):
        if locator.is_enabled():
            break
        page.wait_for_timeout(_SETTLE_MS)
    locator.click(timeout=UI_TIMEOUT)


def _open_appointment_dialog(page: Page, outer, inner, *, client_name, new_client) -> None:
    """Open New -> Appointment, then select an existing client or create one inline.

    The existing-client search occasionally misses on the first try (CRM indexing lag), so the
    open+select is retried (mirrors multistaff). The inline new-client dialog is an Angular
    md-dialog rendered in the frontage (outer) iframe.
    """
    last_error: Exception | None = None
    for attempt in range(3):
        if attempt:
            _dismiss_open_dialog(page, outer)
        new_btn = inner.get_by_role("button", name="New")
        new_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
        new_btn.click()
        appointment_option = inner.get_by_role("menuitem", name="Appointment", exact=True)
        appointment_option.wait_for(state="visible", timeout=UI_TIMEOUT)
        appointment_option.click(timeout=UI_TIMEOUT)
        outer.get_by_role("dialog").wait_for(state="visible", timeout=UI_TIMEOUT)
        try:
            if new_client:
                _create_client_inline(page, outer, new_client)
            else:
                _search_existing_client(page, outer, client_name)
            print("    [dialog] client selected; waiting for service picker")
            inner.locator('[data-qa="service-picker-modal"]:visible').wait_for(
                state="visible", timeout=UI_TIMEOUT
            )
            return
        except PlaywrightTimeoutError as exc:
            print(f"    [dialog] attempt {attempt + 1} failed: {exc}")
            last_error = exc
    raise last_error or AssertionError("Service picker did not open after client selection")


def _search_existing_client(page: Page, outer, client_name: str) -> None:
    search = outer.get_by_role("textbox", name="Search by name, email or tag")
    search.click(timeout=UI_TIMEOUT)
    page.wait_for_timeout(100)
    search.press_sequentially(client_name, delay=30)
    client_option = outer.get_by_role("button").filter(has_text=client_name)
    client_option.wait_for(state="visible", timeout=UI_TIMEOUT)
    client_option.click(timeout=UI_TIMEOUT)


def _create_client_inline(page: Page, outer, new_client: dict) -> None:
    """Open the "New client" dialog from the client picker and save a new client (Angular).

    Scope name fields to the new-client dialog (the appointment dialog underneath also has an
    ``input[name="email"]``). The email field is an autocomplete "dynamic field" that blinks in and
    out and silently drops keystrokes, so it is entered via :func:`_fill_dynamic_email` (fill +
    verify + retry), mirroring legacy ``enterTextToDynamicField``.
    """
    outer.locator(".new-client").first.click(timeout=UI_TIMEOUT)
    dialog = outer.get_by_role("dialog").last
    dialog.locator('input[name="first_name"]').first.fill(new_client["first_name"], timeout=UI_TIMEOUT)
    dialog.locator('input[name="last_name"]').first.fill(new_client.get("last_name", ""), timeout=UI_TIMEOUT)
    _fill_dynamic_email(page, dialog, new_client["email"])
    dialog.get_by_role("button", name="Save").first.click(timeout=UI_TIMEOUT)


_EMAIL_FIELD = 'input[name="email"]'
# The new-client email is an AngularJS md-autocomplete "dynamic field" that perpetually animates
# ("blinks"), so Playwright fill()/type never pass the visibility+stability actionability gate and
# time out, while char-by-char typing is swallowed by the autocomplete. We instead set the value
# straight on the attached node and fire the input/change events that drive ng-model, re-asserting
# until it survives a digest. That needs more than the 5s UI cap (legacy used longSleep + a
# wait-retry loop for exactly this field), so it gets its own documented dynamic-field budget.
_DYN_FIELD_TIMEOUT = 15_000
_SET_INPUT_VALUE_JS = """(node, value) => {
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(node, value);
    node.dispatchEvent(new Event('input', { bubbles: true }));
    node.dispatchEvent(new Event('change', { bubbles: true }));
}"""


def _fill_dynamic_email(page: Page, dialog, email: str) -> None:
    """Set ``email`` on the new-client email field via JS, re-asserting until the value sticks.

    The field is an AngularJS ``md-autocomplete`` that never settles into a stable, visible state,
    so ``fill``/``type`` time out on actionability and char-by-char input is eaten by the
    autocomplete. Setting ``value`` on the attached node and dispatching ``input``/``change`` drives
    ``ng-model`` directly (no actionability gate); we re-set whenever the read-back drifts and only
    return once the value reads back as ``email`` on two consecutive checks (it provably survived a
    digest before Save). Mirrors legacy ``enterTextToDynamicField`` (enter + validate + retry).
    """
    field = dialog.locator(_EMAIL_FIELD).first
    field.wait_for(state="attached", timeout=UI_TIMEOUT)
    deadline = time.time() + _DYN_FIELD_TIMEOUT / 1000
    confirmations = 0
    while time.time() < deadline:
        try:
            node = dialog.locator(_EMAIL_FIELD).first
            if node.input_value(timeout=UI_TIMEOUT) == email:
                confirmations += 1
                if confirmations >= 2:
                    return
            else:
                confirmations = 0
                node.evaluate(_SET_INPUT_VALUE_JS, email)
        except PlaywrightTimeoutError:
            confirmations = 0
        page.wait_for_timeout(_SETTLE_MS)
    raise AssertionError(f"new-client email did not stick within {_DYN_FIELD_TIMEOUT}ms (wanted {email!r})")


def _select_assigned_staff(page: Page, inner, name: str) -> None:
    """Pick an existing staff in the dialog's assigned-staff (.staff-selection) dropdown.

    The option click can be swallowed by the Vuetify ripple overlay, silently leaving the
    default (owner) staff selected (~1/10 under stress). So we fall back to ``dispatch_event``
    and re-open/re-select until the select's displayed text reflects ``name``.
    """
    select = inner.locator(".staff-selection").first
    select.wait_for(state="visible", timeout=UI_TIMEOUT)
    deadline = time.time() + 2 * UI_TIMEOUT / 1000
    while time.time() < deadline:
        try:
            select.click(timeout=UI_TIMEOUT)
            menu = inner.locator(".menuable__content__active").last
            menu.wait_for(state="visible", timeout=UI_TIMEOUT)
            option = menu.locator(".v-list-item", has_text=name).first
            option.wait_for(state="visible", timeout=UI_TIMEOUT)
            try:
                option.click(timeout=UI_TIMEOUT)
            except Exception:  # noqa: BLE001 - Vuetify ripple overlay can swallow the click
                option.dispatch_event("click")
            page.wait_for_timeout(_SETTLE_MS)
            if name in (select.inner_text(timeout=UI_TIMEOUT) or ""):
                return
        except PlaywrightTimeoutError:
            page.wait_for_timeout(_SETTLE_MS)
    raise AssertionError(f"assigned staff {name!r} did not stick in the dialog dropdown")


def _date_input(inner):
    return (
        inner.locator('[data-qa="service-date-input"]').first
        .locator('[data-qa="date-picker-text-input"]').first
    )


def _select_calendar_date(page: Page, inner, target: date) -> None:
    """Navigate the dialog's date-picker popup to ``target`` (past or future) and pick the day."""
    date_input = _date_input(inner)
    before = (date_input.input_value(timeout=UI_TIMEOUT) or "").strip()
    date_input.click(timeout=UI_TIMEOUT)

    menu = inner.locator(".date-picker-menu-content")
    header = menu.locator(".v-date-picker-header__value").first
    menu.locator(".v-date-picker-table--date").first.wait_for(state="visible", timeout=UI_TIMEOUT)

    target_label = target.strftime("%B %Y").lower()
    for _ in range(25):  # bounded both directions (>1 year headroom)
        current = (header.inner_text(timeout=UI_TIMEOUT) or "").lower()
        if target_label in current:
            break
        # header buttons: first = previous month, last = next month
        forward = _parse_header_date(current) is None or _parse_header_date(current) < target
        button = menu.locator(".v-date-picker-header button")
        (button.last if forward else button.first).click(timeout=UI_TIMEOUT)
        page.wait_for_timeout(_SETTLE_MS)

    page.wait_for_timeout(_SETTLE_MS)  # let the month-change transition finish
    # Use the visible day table (a transition can briefly leave a stale table in the DOM).
    table = menu.locator(".v-date-picker-table--date:visible").last
    day_cells = table.locator("button.v-btn").filter(has_text=re.compile(rf"^\s*{target.day}\s*$"))
    cell = day_cells.first if target.day <= 14 else day_cells.last
    cell.wait_for(state="visible", timeout=UI_TIMEOUT)
    try:
        cell.click(timeout=UI_TIMEOUT)
    except Exception:  # noqa: BLE001 - Vuetify ripple overlay can swallow the click
        cell.dispatch_event("click")

    for _ in range(int(UI_TIMEOUT / _SETTLE_MS)):
        after = (date_input.input_value() or "").strip()
        if after and after != before:
            return
        page.wait_for_timeout(_SETTLE_MS)
    raise AssertionError(f"Appointment date did not change to {target:%Y-%m-%d} (still {before!r})")


def _parse_header_date(header_text: str) -> date | None:
    try:
        return datetime.strptime(header_text.strip(), "%B %Y").date().replace(day=1)
    except ValueError:
        return None


def _toggle_all_day(page: Page, inner) -> None:
    _date_input(inner).click(timeout=UI_TIMEOUT)
    switch = inner.locator("[label='All day']").first
    switch.wait_for(state="visible", timeout=UI_TIMEOUT)
    state_input = inner.locator(
        ".switch-container .v-input__slot .v-input--selection-controls__input input"
    ).first
    if (state_input.get_attribute("aria-checked") or "false") != "true":
        switch.click(timeout=UI_TIMEOUT)
        page.wait_for_timeout(_SETTLE_MS)


def _select_time(inner, kind: str, label: str) -> None:
    """Pick a start/end time from the dialog dropdown (data-qa item label, e.g. '01:00 AM').

    Scope the option lookup to the currently-open menu (``menuable__content__active``):
    both the start and end time menus keep their items in the DOM, so an unscoped
    ``[data-qa='item-...']`` would match a hidden item in the other (closed) menu.
    """
    inner.locator(f'[data-qa="service-{kind}-time-input"] input').first.click(timeout=UI_TIMEOUT)
    menu = inner.locator(".menuable__content__active").last
    menu.wait_for(state="visible", timeout=UI_TIMEOUT)
    for candidate in _time_label_variants(label):
        option = menu.locator(f'[data-qa="item-{candidate}"]').first
        if option.count() > 0:
            option.scroll_into_view_if_needed(timeout=UI_TIMEOUT)
            option.click(timeout=UI_TIMEOUT)
            return
    raise AssertionError(f"{kind} time option {label!r} not found in the open time dropdown")


def _time_label_variants(label: str) -> list[str]:
    """Legacy passes labels verbatim ('01:00 AM'); also try the no-leading-zero form ('1:00 AM')."""
    variants = [label]
    stripped = re.sub(r"^0(\d:)", r"\1", label)
    if stripped != label:
        variants.append(stripped)
    return variants


_RECIPIENTS_PANEL = ".dialog-expansion-panel__additional-recipients"
_RECIPIENTS_COMBOBOX = "[data-qa='additional-recipients-combobox']"


def _add_additional_recipients(page: Page, inner, recipients: str) -> None:
    """Add an additional recipient (typed email or "from list") in the dialog's panel.

    Mirrors legacy createMeetingDialog.addAdditionalRecipients: expand the panel, open the
    combobox, then either pick the first existing option ("from list") or type the email and
    commit it as a chip (the legacy value carries a trailing comma to commit the chip).
    """
    combobox = inner.locator(_RECIPIENTS_COMBOBOX).first
    if not combobox.is_visible():
        inner.locator(f"{_RECIPIENTS_PANEL} .v-expansion-panel-header").first.click(timeout=UI_TIMEOUT)
        combobox.wait_for(state="visible", timeout=UI_TIMEOUT)
    combobox.click(timeout=UI_TIMEOUT)

    if recipients.strip().lower() == "from list":
        option = inner.locator(
            ".menuable__content__active.v-autocomplete__content [tabindex='0']"
        ).first
        option.wait_for(state="visible", timeout=UI_TIMEOUT)
        option.click(timeout=UI_TIMEOUT)
        return

    # The combobox click above focuses its input (data-qa sits on the input/wrapper, so a
    # nested `input` lookup can miss); type into the focused field and commit the chip.
    page.keyboard.type(recipients.rstrip(","), delay=20)
    page.keyboard.press("Enter")
    page.wait_for_timeout(_SETTLE_MS)


def _choose_vuetify_option(inner, select_selector: str, option_label: str) -> None:
    """Open a Vuetify select and click the option matching ``option_label`` in the active menu."""
    inner.locator(select_selector).first.click(timeout=UI_TIMEOUT)
    menu = inner.locator(".menuable__content__active").last
    menu.wait_for(state="visible", timeout=UI_TIMEOUT)
    option = menu.locator(".v-list-item", has_text=re.compile(rf"^\s*{re.escape(option_label)}\s*$")).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click(timeout=UI_TIMEOUT)


def _add_arrival_window(page: Page, inner, arrival_window: str) -> None:
    """Set the arrival window in the dialog (legacy createMeetingDialog.addArrivalWindow).

    A preset (e.g. "2 hours", "30 minutes") is chosen directly. "Custom <minutes>" picks the
    Custom option then sets the hours/minutes sub-selects (e.g. 75 -> 1 hours + 15 minutes).
    """
    parts = arrival_window.split(" ")
    if parts[0] != "Custom":
        _choose_vuetify_option(inner, ".arrival-window-dropdown", arrival_window)
    else:
        total = int(parts[1])
        _choose_vuetify_option(inner, ".arrival-window-dropdown", "Custom")
        _choose_vuetify_option(inner, ".custom-arrival-window-hours", f"{total // 60} hours")
        _choose_vuetify_option(inner, ".custom-arrival-widow-minutes", f"{total % 60} minutes")
    page.wait_for_timeout(_SETTLE_MS)


def _enable_client_confirmation(inner) -> None:
    checkbox = inner.locator("div[data-qa='require-confirmation-checkbox'] input").first
    checkbox.wait_for(state="visible", timeout=UI_TIMEOUT)
    if (checkbox.get_attribute("aria-checked") or "false") != "true":
        checkbox.click(timeout=UI_TIMEOUT)


def open_meeting_page(page: Page, appointment_id: str):
    """Navigate to the appointment detail page and return the Angular frame locator."""
    page.goto(
        f"{_app_base(page)}/app/appointments/{appointment_id}",
        wait_until="domcontentloaded",
        timeout=UI_TIMEOUT,
    )
    page.wait_for_selector('iframe[title="angularjs"]', state="visible", timeout=UI_TIMEOUT)
    outer = page.frame_locator('iframe[title="angularjs"]')
    outer.locator("[data-qa='appointment-state']").first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return outer


def reschedule_appointment(
    page: Page,
    appointment_id: str,
    *,
    new_date: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    arrival_window: str | None = None,
) -> None:
    """Reschedule via the detail-page dialog (legacy rescheduleDialog.proposeANewTime).

    Sets an arrival window (``.arrival-window-select``) and/or a new Kendo start/end datetime.
    """
    outer = open_meeting_page(page, appointment_id)
    outer.locator('[data-qa="reschedule"]').first.click(timeout=UI_TIMEOUT)
    dialog = outer.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=UI_TIMEOUT)

    if arrival_window:
        _choose_arrival_window_select(outer, arrival_window)

    if new_date or start_time or end_time:
        target = resolve_meeting_date(new_date)
        start_value = f"{target.strftime('%a')} {target.month}/{target.day}/{target.year} {start_time}"
        end_value = f"{target.strftime('%a')} {target.month}/{target.day}/{target.year} {end_time}"
        _type_kendo_datetime(outer, ".start-time", start_value)
        _type_kendo_datetime(outer, ".end-time", end_value)

    submit = outer.get_by_role("button", name="Submit").first
    _click_when_enabled(page, submit)
    # The dialog closes on a successful reschedule (arrival-only or datetime); the caller's
    # assert_meeting re-navigates and verifies the result, so don't depend on the conditional
    # "Rescheduled from" note (it only renders when a new date/time was set).
    submit.wait_for(state="hidden", timeout=UI_TIMEOUT)


def _choose_arrival_window_select(outer, option_label: str) -> None:
    """Pick an arrival-window option in the (Angular md-select) reschedule dialog."""
    outer.locator(".arrival-window-select").first.click(timeout=UI_TIMEOUT)
    outer.locator("md-option", has_text=re.compile(rf"^\s*{re.escape(option_label)}\s*$")).first.click(
        timeout=UI_TIMEOUT
    )


def _type_kendo_datetime(outer, container: str, value: str) -> None:
    field = outer.locator(f"{container} .k-picker-wrap input").first
    field.click(timeout=UI_TIMEOUT)
    field.fill(value, timeout=UI_TIMEOUT)
    outer.locator(".reschedule-message").first.click(timeout=UI_TIMEOUT)


def cancel_appointment(page: Page, appointment_id: str) -> None:
    """Cancel the appointment from the detail page and wait for the CANCELLED state."""
    outer = open_meeting_page(page, appointment_id)
    outer.locator('[data-qa="cancel"]').first.click(timeout=UI_TIMEOUT)
    outer.get_by_role("dialog").wait_for(state="visible", timeout=UI_TIMEOUT)
    _click_when_enabled(page, outer.get_by_role("button", name="Submit").first)
    outer.get_by_text("Cancelled", exact=True).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def meeting_state(outer) -> str:
    return meeting_text(outer, "appointment-state")


def meeting_datetime_text(outer) -> str:
    return meeting_text(outer, "appointment-date")


def assert_meeting(
    page: Page,
    appointment_id: str,
    *,
    service_name: str,
    client_name: str,
    state: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    additional_recipients: str | None = None,
    assigned_staff: str | None = None,
    meeting_date: str | None = None,
    arrival_window: str | None = None,
) -> None:
    """Open the detail page and assert service, client, state, times, staff, recipients (as given)."""
    outer = open_meeting_page(page, appointment_id)
    header = (outer.locator("div.summary-header h3").first.inner_text() or "").strip()
    client_text = meeting_text(outer, "display-name")
    datetime_text = meeting_datetime_text(outer).lower()

    if meeting_date:
        target = resolve_meeting_date(meeting_date)
        month_abbr = target.strftime("%b").lower()
        assert month_abbr in datetime_text and str(target.day) in datetime_text, (
            f"expected date ~{target:%b %d} in date row, got {datetime_text!r}"
        )

    assert service_name in header, f"expected service '{service_name}' in header, got {header!r}"
    assert client_name.lower() in client_text.lower(), f"expected client '{client_name}', got {client_text!r}"
    if assigned_staff:
        staff_text = meeting_text(outer, "assigned-staff")
        assert assigned_staff in staff_text, f"expected assigned staff '{assigned_staff}', got {staff_text!r}"
    if state:
        state_text = meeting_state(outer)
        assert state.upper() in state_text.upper(), f"expected state '{state}', got {state_text!r}"
    for label, value in (("start", start_time), ("end", end_time)):
        if value:
            needle = value.replace(" ", "").lower()
            assert needle in datetime_text.replace(" ", ""), (
                f"expected {label} time '{value}' in date row, got {datetime_text!r}"
            )
    if additional_recipients:
        recipients_text = meeting_text(outer, "additional-recipients")
        assert additional_recipients in recipients_text, (
            f"expected recipient '{additional_recipients}', got {recipients_text!r}"
        )
    if arrival_window:
        arrival_el = outer.locator(".arrival-window-time").first
        arrival_el.wait_for(state="visible", timeout=UI_TIMEOUT)
        arrival_text = (arrival_el.inner_text() or "").strip().lower()
        expected = arrival_window.strip().lower()
        assert expected in arrival_text, (
            f"expected arrival window '{arrival_window}', got {arrival_text!r}"
        )
