from __future__ import annotations

from datetime import datetime, timedelta
import re
from typing import Any

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from tests.scheduling.appointments.appointment_helpers import open_calendar_page

UI_TIMEOUT = 5_000
VIEW_OPTIONS = {
    "Month": "option-month",
    "Week": "option-week",
    "3 Days": "option-threeDay",
    "Day": "option-singleDay",
    "Agenda": "option-agenda",
}
DISPLAY_STATE = {
    "Month": "month",
    "Week": "week",
    "3 Days": "threeDay",
    "Day": "singleDay",
    "Agenda": "agenda",
}
THREE_DAY_COLUMN = {"left": 0, "middle": 1, "right": 2}


def schedule_appointment_from_calendar(page: Page, context: dict, params: dict[str, str]) -> None:
    angular, vue = navigate_calendar(page, params["display"], params.get("navigate_to"))
    choose_calendar_slot(vue, params["display"], params["timeslot"], params.get("timeslot_end"))
    vue.locator('[data-qa="option-new_appointment"]').click(timeout=UI_TIMEOUT)

    _select_client(angular, params["client_name"])
    service_picker = vue.locator('[data-qa="service-picker-modal"]:visible')
    service_picker.wait_for(state="visible", timeout=UI_TIMEOUT)
    service_picker.locator(".service-item").filter(has_text=context["calendar_services"][params["service_name"]]["name"]).first.locator(
        '[data-qa="service-name"]'
    ).click(timeout=UI_TIMEOUT)
    service_picker.wait_for(state="hidden", timeout=UI_TIMEOUT)

    _set_appointment_fields(vue, params, context)
    print(f"  Calendar: submitting appointment {params['meeting_identifier']}...")
    button = vue.get_by_role("button", name=re.compile(r"Schedule\s*appointment|^Schedule$", re.I)).last
    button.wait_for(state="visible", timeout=UI_TIMEOUT)
    button.scroll_into_view_if_needed(timeout=UI_TIMEOUT)
    button.click(force=True, timeout=UI_TIMEOUT)
    print(f"  Calendar: appointment {params['meeting_identifier']} submit clicked")
    _wait_for_appointment_submit(vue, params)
    context.setdefault("calendar_bookings", {})[params["meeting_identifier"]] = params


def schedule_event_from_calendar(page: Page, context: dict, params: dict[str, str]) -> None:
    _, vue = navigate_calendar(page, params["display"], params.get("navigate_to"))
    choose_calendar_slot(vue, params["display"], params["timeslot"])
    vue.locator('[data-qa="option-new_event"]').click(timeout=UI_TIMEOUT)
    dialog = vue.locator(".event-dialog-container, [data-qa='did-mount']").first
    dialog.wait_for(state="visible", timeout=UI_TIMEOUT)

    _choose_select_option(vue, vue.locator('[data-qa="service-select-input"]').first, context["calendar_services"][params["service_name"]]["name"])
    if params.get("recurrence"):
        vue.locator(".recurrence-string").click(timeout=UI_TIMEOUT)
        _set_recurrence(vue, params["recurrence"], params.get("ends", ""))
    if params.get("meeting_date"):
        _select_relative_date(vue, params["meeting_date"])
    if params.get("start_time"):
        _select_time(vue, "service-start-time-input", params["start_time"])
    if params.get("end_time"):
        _select_time(vue, "service-end-time-input", params["end_time"])

    submit = vue.locator("button[data-qa='dialog-submit-button']:not([disabled])").first
    submit.wait_for(state="visible", timeout=UI_TIMEOUT)
    submit.click(timeout=UI_TIMEOUT)
    if params.get("recurrence"):
        _wait_for_dialog_to_close(vue)
    else:
        page.wait_for_url("**/app/events/**", timeout=UI_TIMEOUT)
    context.setdefault("calendar_events", {})[params.get("event_identifier") or params["service_name"]] = params


def set_content_display(page: Page, interval: str | None = None, slot_colors: str | None = None) -> None:
    _, vue = get_calendar_frames(page)
    vue.locator('[data-qa="scheduler-settings-dropdown-activator"] [data-qa]').first.click(timeout=UI_TIMEOUT)
    vue.locator('[data-qa="option-open-content-display-settings"]').click(timeout=UI_TIMEOUT)
    vue.locator('[data-qa="content-display-layout_save-mobile"]').wait_for(state="visible", timeout=UI_TIMEOUT)
    if interval:
        vue.get_by_text(interval, exact=True).click(timeout=UI_TIMEOUT)
    if slot_colors:
        vue.locator(f'[data-qa="radio-{slot_colors}"]').click(timeout=UI_TIMEOUT)
    save_button = vue.locator('[data-qa="content-display-layout_save-mobile"]').first
    if save_button.is_enabled():
        save_button.click(timeout=UI_TIMEOUT)
        vue.locator('button[data-qa="content-display-layout_save-mobile"][disabled]').wait_for(state="visible", timeout=UI_TIMEOUT)
    vue.locator(".icon-close_new").first.click(force=True, timeout=UI_TIMEOUT)
    vue.get_by_text("Content Display", exact=True).wait_for(state="hidden", timeout=UI_TIMEOUT)


def add_blocked_time(page: Page, params: dict[str, str]) -> None:
    _, vue = navigate_calendar(page, params["display"], params.get("navigate_to"))
    choose_calendar_slot(vue, params["display"], params["timeslot"], params.get("timeslot_end"))
    vue.locator('[data-qa="option-block_off_time"]').click(timeout=UI_TIMEOUT)
    dialog = vue.locator('[data-qa="did-mount"]').first
    dialog.wait_for(state="visible", timeout=UI_TIMEOUT)
    if params.get("title"):
        title_input = vue.locator('.custom-title-input [data-qa="vc-text-field"]').first
        title_input.fill(params["title"])
    if params.get("additional_staffs"):
        vue.locator(".staff-picker-button").click(timeout=UI_TIMEOUT)
        for staff in params["additional_staffs"].split(","):
            vue.locator(f'[data-qa="staff-{staff.strip()}"]').click(timeout=UI_TIMEOUT)
        vue.locator("body").press("Escape")
        vue.get_by_text("Block off time", exact=True).click(timeout=UI_TIMEOUT)
    vue.locator(".submit-button").click(timeout=UI_TIMEOUT)
    _wait_for_dialog_to_close(vue)


def drag_calendar_item(page: Page, title: str, display: str, direction: str, new_timeslot: str) -> None:
    _, vue = navigate_calendar(page, display, direction)
    item = vue.locator(".smart-scheduler-event-content.vc-event").filter(has_text=title).first
    target = _slot_locator(vue, display, new_timeslot)
    item.wait_for(state="visible", timeout=UI_TIMEOUT)
    target.wait_for(state="visible", timeout=UI_TIMEOUT)
    item.drag_to(target, timeout=UI_TIMEOUT)
    wait_for_calendar_idle(vue)


def edit_blocked_time(page: Page, old_title: str, new_title: str, new_start_time: str) -> None:
    _, vue = get_calendar_frames(page)
    item = vue.locator(f'[data-qa="meeting-{old_title}"]').first
    if item.count() == 0:
        item = vue.locator(".smart-scheduler-event-content.vc-event").filter(has_text=old_title).first
    item.click(timeout=UI_TIMEOUT)
    dialog = vue.locator('[data-qa="did-mount"]').first
    dialog.wait_for(state="visible", timeout=UI_TIMEOUT)
    vue.locator('.custom-title-input [data-qa="vc-text-field"]').fill(new_title)
    _select_time(vue, "service-start-time-input", new_start_time)
    vue.locator(".submit-button").click(timeout=UI_TIMEOUT)
    _wait_for_dialog_to_close(vue)


def select_staff_filter(page: Page, staff_name: str) -> None:
    _, vue = get_calendar_frames(page)
    staff_list = vue.locator(".staff-list-container")
    staff_list.wait_for(state="visible", timeout=UI_TIMEOUT)
    if staff_name == "all":
        staff_list.locator(".staff-item-container").evaluate_all(
            """items => {
                for (const item of items) {
                    const input = item.querySelector('input[type="checkbox"]');
                    const label = item.querySelector('label');
                    if (input && label && !input.checked) label.click();
                }
            }"""
        )
        wait_for_calendar_idle(vue)
        return

    staff_list.locator(".staff-item-container").evaluate_all(
        """items => {
            for (const item of items) {
                const input = item.querySelector('input[type="checkbox"]');
                const label = item.querySelector('label');
                if (input && label && input.checked) label.click();
            }
        }"""
    )
    try:
        vue.locator(f'[data-qa="staff-item-{staff_name}"] label').click(timeout=5_000)
    except PlaywrightTimeoutError:
        staff_list.locator(".staff-item-container").filter(has_text=staff_name).first.locator("label").click(timeout=UI_TIMEOUT)
    wait_for_calendar_idle(vue)


def assert_calendar_items(page: Page, direction: str, display: str, expected: list[dict[str, str]]) -> None:
    _, vue = navigate_calendar(page, display, direction)
    last_items: list[dict[str, Any]] = []
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    while datetime.now().timestamp() < deadline:
        last_items = parse_calendar_items(vue, display)
        if _items_match(last_items, expected):
            return
        page.wait_for_timeout(500)
    raise AssertionError(f"Calendar items did not match.\nExpected: {expected}\nActual: {last_items}")


def assert_current_display_state(page: Page, expected_display_type: str, expected_display_time: str) -> None:
    _, vue = get_calendar_frames(page)
    wait_for_calendar_idle(vue)
    state = vue.locator("smart-scheduler.smart-element.smart-scheduler").get_attribute("view")
    actual_distance = vue.locator("span.header-actions_start_current-dates").evaluate(
        """(el, expectedView) => {
            const text = el.textContent.trim();
            const now = new Date();
            now.setHours(0, 0, 0, 0);
            function parseHeaderDate() {
              if (expectedView === 'singleDay') return new Date(`${text}, ${now.getFullYear()}`);
              if (expectedView === 'month') return new Date(text);
              const [startRange, endRange] = text.split(' - ');
              const monthAndDay = startRange.split(',')[0];
              const year = startRange.split(',').length === 1 ? endRange.split(', ')[1] : startRange.split(', ')[1];
              return new Date(`${monthAndDay}, ${year}`);
            }
            const calendarDate = parseHeaderDate();
            if (expectedView === 'week') now.setDate(now.getDate() - now.getDay());
            const dayDiff = Math.ceil((calendarDate - now) / 86400000);
            if (expectedView === 'month') {
              return String(calendarDate.getFullYear() * 12 + calendarDate.getMonth() - now.getFullYear() * 12 - now.getMonth());
            }
            if (expectedView === 'week') return String(dayDiff / 7);
            if (expectedView === 'threeDay') return String(dayDiff / 3);
            return String(dayDiff);
        }""",
        expected_display_type,
    )
    assert state == expected_display_type
    assert actual_distance == expected_display_time


def trigger_calendar_print(page: Page) -> None:
    _, vue = get_calendar_frames(page)
    _select_view(vue, "Month")
    with page.expect_download(timeout=UI_TIMEOUT) as download_info:
        vue.locator('[data-qa="scheduler-additional-action-dropdown-activator"]').click(timeout=UI_TIMEOUT)
        vue.locator('[data-qa="option-print"]').click(timeout=UI_TIMEOUT)
    download = download_info.value
    if "Calendar View" not in download.suggested_filename:
        raise AssertionError(f"Unexpected calendar download name: {download.suggested_filename}")


def navigate_calendar(page: Page, display: str, direction: str | None = None):
    open_calendar_page(page)
    angular, vue = get_calendar_frames(page)
    wait_for_calendar_idle(vue)
    vue.locator('[data-qa="today-button"], [data-qa="nav-today"]').click(timeout=UI_TIMEOUT)
    _select_view(vue, display)
    if direction in ("next", "previous"):
        button = "next-button" if direction == "next" else "prev-button"
        nav_alias = "next" if direction == "next" else "prev"
        vue.locator(f'[data-qa="{button}"], [data-qa="nav-{nav_alias}"]').click(timeout=UI_TIMEOUT)
    wait_for_calendar_idle(vue)
    return angular, vue


def get_calendar_frames(page: Page):
    page.wait_for_selector('iframe[title="angularjs"]', timeout=UI_TIMEOUT)
    angular_handle = page.locator('iframe[title="angularjs"]').element_handle()
    if not angular_handle:
        raise AssertionError("Angular iframe was not found")
    angular = angular_handle.content_frame()
    if not angular:
        raise AssertionError("Angular iframe content was not available")
    vue_handle = angular.locator("#vue_iframe_layout").element_handle(timeout=UI_TIMEOUT)
    if not vue_handle:
        raise AssertionError("Vue scheduler iframe was not found")
    vue = vue_handle.content_frame()
    if not vue:
        raise AssertionError("Vue scheduler iframe content was not available")
    return angular, vue


def choose_calendar_slot(vue, display: str, timeslot: str, timeslot_end: str | None = None) -> None:
    slot = _slot_locator(vue, display, timeslot)
    slot.wait_for(state="visible", timeout=UI_TIMEOUT)
    if not timeslot_end:
        slot.click(timeout=UI_TIMEOUT)
    else:
        end_slot = _slot_locator(vue, display, timeslot_end)
        end_slot.wait_for(state="visible", timeout=UI_TIMEOUT)
        slot.drag_to(end_slot, timeout=UI_TIMEOUT)
    vue.locator(".v-menu__content.menuable__content__active").wait_for(state="visible", timeout=UI_TIMEOUT)


def wait_for_calendar_idle(vue) -> None:
    vue.locator(".vcita-scheduler").wait_for(state="visible", timeout=UI_TIMEOUT)
    try:
        vue.locator('[data-qa="scheduler-loader"]').wait_for(state="hidden", timeout=UI_TIMEOUT)
    except PlaywrightTimeoutError:
        pass


def parse_calendar_items(vue, display: str) -> list[dict[str, str]]:
    time_selector = ".event-time" if display in ("Month", "Agenda") else ".event-timespan"
    return vue.locator(".smart-scheduler-event-content.vc-event").evaluate_all(
        """(nodes, timeSelector) => {
            const seen = new Set();
            return nodes.map(node => {
                const parent = node.parentElement;
                const id = parent ? parent.id : '';
                if (id && seen.has(id)) return null;
                if (id) seen.add(id);
                const classes = node.className || '';
                const typeMatch = classes.match(/event-type-(\\w*)/);
                const colorMatch = classes.match(/color-(\\w*)/);
                const typeMap = { Appointment: 'appointment', EventInstance: 'event', CalendarSyncItem: 'sync_item', BlockedTime: 'blocked_time' };
                const itemType = typeMap[typeMatch && typeMatch[1]] || typeMatch && typeMatch[1] || '';
                const text = selector => (node.querySelector(selector)?.textContent || '').trim();
                return {
                    item_type: itemType,
                    state: node.getAttribute('data-state') || '',
                    item_title: itemType === 'event' ? '' : text('.event-title'),
                    item_subtitle: text('.event-subtitle, .event-subtitle b'),
                    attendance: itemType === 'event' ? text('.event-title span') : '',
                    item_times: text(timeSelector),
                    color: colorMatch ? colorMatch[1] : '',
                };
            }).filter(Boolean);
        }""",
        time_selector,
    )


def _slot_locator(vue, display: str, timeslot: str):
    if display == "Month":
        return vue.locator(f'.smart-scheduler-cell[date*="{timeslot} 2"]:not([other-month])').first
    if display == "Week":
        return vue.locator(f'[data-qa="{timeslot}"]').first
    if display == "3 Days":
        column, hour = [part.strip() for part in timeslot.split(",", 1)]
        return vue.locator(f'.smart-scheduler-cell[data-qa*="{hour}"]').nth(THREE_DAY_COLUMN[column])
    if display == "Day" and timeslot == "all_day":
        return vue.locator('.smart-scheduler-cell[data-all-day="true"]').first
    return vue.locator(f'.smart-scheduler-cell[data-qa*="{timeslot}"]').first


def _select_client(angular, client_name: str) -> None:
    search = angular.get_by_role("textbox", name="Search by name, email or tag")
    search.wait_for(state="visible", timeout=UI_TIMEOUT)
    search.fill("")
    search.press_sequentially(client_name, delay=25)
    angular.get_by_role("button").filter(has_text=client_name).first.click(timeout=UI_TIMEOUT)


def _set_appointment_fields(vue, params: dict[str, str], context: dict) -> None:
    if params.get("assigned_staff"):
        _choose_select_option(vue, vue.locator(".staff-selection").first, params["assigned_staff"])
    if params.get("meeting_date"):
        _select_relative_date(vue, params["meeting_date"])
    if params.get("switch_all_day") == "all_day":
        vue.locator('[data-qa="date-picker-text-input"]').click(timeout=UI_TIMEOUT)
        all_day_input = vue.locator(".switch-container input").first
        checked = all_day_input.is_checked()
        if not checked:
            vue.get_by_text("All day", exact=True).click(timeout=UI_TIMEOUT)
        vue.locator("body").press("Escape")
    if params.get("start_time"):
        _select_time(vue, "service-start-time-input", params["start_time"])
    if params.get("end_time"):
        _select_time(vue, "service-end-time-input", params["end_time"])
    if params.get("client_confirmation") == "Checked":
        checkbox = vue.locator("div[data-qa='require-confirmation-checkbox'] input").first
        if not checkbox.is_checked():
            checkbox.click(force=True)


def _select_time(vue, data_qa: str, time_text: str) -> None:
    vue.locator(f'[data-qa="{data_qa}"]').first.click(timeout=UI_TIMEOUT)
    vue.locator(f'div.menuable__content__active div button[data-qa="item-{time_text}"]').first.click(timeout=UI_TIMEOUT)


def _select_relative_date(vue, date_key: str) -> None:
    if not date_key:
        return
    offsets = {"next_week": 7, "last_week": -7, "next_day": 1, "last_day": -1}
    if date_key not in offsets:
        return
    target_day = (datetime.now() + timedelta(days=offsets[date_key])).day
    vue.locator('[data-qa="date-picker-text-input"]').click(timeout=UI_TIMEOUT)
    vue.locator(".date-picker-menu-content button").filter(has_text=str(target_day)).last.click(timeout=UI_TIMEOUT)


def _select_view(vue, display: str) -> None:
    expected_view = DISPLAY_STATE[display]
    scheduler = vue.locator("smart-scheduler.smart-element.smart-scheduler")
    if scheduler.get_attribute("view") == expected_view:
        return
    vue.locator('[data-qa="view-button"]').click(timeout=UI_TIMEOUT)
    vue.locator(f'[data-qa="{VIEW_OPTIONS[display]}"]').click(timeout=UI_TIMEOUT)
    expect(scheduler).to_have_attribute("view", expected_view, timeout=UI_TIMEOUT)


def _choose_select_option(vue, select_locator, option_text: str) -> None:
    select_locator.click(timeout=UI_TIMEOUT)
    vue.get_by_text(option_text, exact=True).last.click(timeout=UI_TIMEOUT)


def _set_recurrence(vue, recurrence: str, ends: str) -> None:
    amount, unit = recurrence.split(" ", 1)
    switch = vue.locator(".recurrence-switch").first
    if switch.count() > 0:
        switch.click(timeout=UI_TIMEOUT)
    _choose_select_option(vue, vue.locator(".recurrence-type-select").first, unit)
    vue.locator(".frequency-input input").first.fill(amount)
    if ends.startswith("After:"):
        _choose_select_option(vue, vue.locator(".end-type-select").first, "After")
        vue.locator(".times-input input").first.fill(ends.split(":", 1)[1])
    vue.locator(".recurrence-footer .done-btn").click(timeout=UI_TIMEOUT)


def _wait_for_dialog_to_close(vue) -> None:
    try:
        vue.get_by_role("dialog").first.wait_for(state="hidden", timeout=UI_TIMEOUT)
    except PlaywrightTimeoutError:
        wait_for_calendar_idle(vue)


def _wait_for_appointment_submit(vue, params: dict[str, str]) -> None:
    dialog = vue.get_by_role("dialog").first
    created_in_past = params.get("navigate_to") == "previous" or params.get("meeting_date") in {"last_week", "last_day"}
    requires_confirmation = params.get("client_confirmation") == "Checked"
    if not created_in_past and not requires_confirmation:
        try:
            dialog.wait_for(state="hidden", timeout=3_000)
        except PlaywrightTimeoutError:
            _close_active_dialog(vue, dialog)
        return
    try:
        dialog.wait_for(state="hidden", timeout=3_000)
    except PlaywrightTimeoutError:
        _close_active_dialog(vue, dialog)


def _close_active_dialog(vue, dialog) -> None:
    if not dialog.is_visible():
        return
    vue.locator("body").press("Escape")
    try:
        dialog.wait_for(state="hidden", timeout=1_000)
        return
    except PlaywrightTimeoutError:
        pass
    try:
        vue.get_by_role("button", name="Cancel").click(force=True, timeout=3_000)
        dialog.wait_for(state="hidden", timeout=1_000)
        return
    except PlaywrightTimeoutError:
        pass
    dialog.locator(".v-icon, .icon-close_new").last.click(force=True, timeout=UI_TIMEOUT)


def _items_match(actual: list[dict[str, str]], expected: list[dict[str, str]]) -> bool:
    if len(actual) < len(expected):
        return False
    used_indexes: set[int] = set()
    for expected_item in expected:
        match_index = _find_matching_item(actual, expected_item, used_indexes)
        if match_index is None:
            return False
        used_indexes.add(match_index)
    return True


def _find_matching_item(actual: list[dict[str, str]], expected_item: dict[str, str], used_indexes: set[int]) -> int | None:
    for index, actual_item in enumerate(actual):
        if index in used_indexes:
            continue
        if all(
            value == "" or str(actual_item.get(key, "")).strip() == str(value).strip()
            for key, value in expected_item.items()
        ):
            return index
    return None
