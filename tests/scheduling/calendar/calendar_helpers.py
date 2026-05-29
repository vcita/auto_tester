from __future__ import annotations

from datetime import datetime, timedelta
import re
from typing import Any
from urllib.parse import quote

from playwright.sync_api import Error as PlaywrightError, Page, TimeoutError as PlaywrightTimeoutError, expect

from tests.scheduling.appointments.appointment_helpers import open_calendar_page
from tests.scheduling.calendar.calendar_api import get_sso_token, resolve_partner_base_url, staff_uid

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
    slot_date = None
    for attempt in range(3):
        angular, vue = navigate_calendar(page, params["display"], params.get("navigate_to"))
        choose_calendar_slot(vue, params["display"], params["timeslot"], params.get("timeslot_end"))
        slot_date = _slot_date(params["display"], params.get("navigate_to", "current"), params["timeslot"])
        vue.locator('[data-qa="option-new_appointment"]').click(timeout=UI_TIMEOUT)
        try:
            _select_client(angular, params["client_name"])
            break
        except PlaywrightTimeoutError:
            if attempt == 2:
                raise
            page.reload(wait_until="domcontentloaded", timeout=UI_TIMEOUT)
            open_calendar_page(page)

    service_picker = vue.locator('[data-qa="service-picker-modal"]:visible')
    service_picker.wait_for(state="visible", timeout=UI_TIMEOUT)
    service_picker.locator(".service-item").filter(has_text=context["calendar_services"][params["service_name"]]["name"]).first.locator(
        '[data-qa="service-name"]'
    ).click(timeout=UI_TIMEOUT)
    service_picker.wait_for(state="hidden", timeout=UI_TIMEOUT)

    _set_appointment_fields(vue, params, context, slot_date)
    print(f"  Calendar: submitting appointment {params['meeting_identifier']}...")
    dialog = vue.get_by_role("dialog").first
    _wait_and_click_visible_appointment_submit(vue)
    print(f"  Calendar: appointment {params['meeting_identifier']} submit clicked")
    _wait_for_appointment_submit(vue, params)
    if params.get("client_confirmation") == "Checked":
        open_calendar_page(page)
    context.setdefault("calendar_bookings", {})[params["meeting_identifier"]] = params


def schedule_event_from_calendar(page: Page, context: dict, params: dict[str, str]) -> None:
    _, vue = navigate_calendar(page, params["display"], params.get("navigate_to"))
    choose_calendar_slot(vue, params["display"], params["timeslot"], params.get("timeslot_end"))
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
        _wait_for_button_disabled(save_button)
    _close_settings_side_pane(page, vue)


def _close_settings_side_pane(page: Page, vue) -> None:
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    closed_polls = 0
    while datetime.now().timestamp() < deadline:
        has_visible_pane = False
        for frame in page.frames:
            has_visible_pane = frame.evaluate(
                """() => {
                    const root = document.querySelector('#app')?.__vue__;
                    const stack = root ? [root] : [];
                    while (stack.length) {
                        const vm = stack.pop();
                        if (Object.prototype.hasOwnProperty.call(vm, 'settingsSidePainOptions')) {
                            vm.settingsSidePainOptions = null;
                        }
                        if (typeof vm.closeOpenSidePane === 'function') {
                            vm.closeOpenSidePane();
                        }
                        stack.push(...(vm.$children || []));
                    }
                    const panes = Array.from(document.querySelectorAll('.calendar-settings-sid-pane'));
                    for (const pane of panes) {
                        const closeButton =
                            pane.querySelector('.calendar-settings-sid-pane__panel__header__button button:last-child') ||
                            Array.from(pane.querySelectorAll('button')).at(-1);
                        closeButton?.click();
                        pane.style.setProperty('display', 'none', 'important');
                        pane.style.setProperty('width', '0px', 'important');
                        pane.style.setProperty('pointer-events', 'none', 'important');
                    }
                    for (const title of Array.from(document.querySelectorAll('body *')).filter((node) => {
                        return (node.innerText || '').trim() === 'Content Display';
                    })) {
                        const drawer = title.closest('.v-navigation-drawer, .calendar-settings-sid-pane');
                        if (drawer) {
                            drawer.style.setProperty('display', 'none', 'important');
                            drawer.style.setProperty('width', '0px', 'important');
                            drawer.style.setProperty('pointer-events', 'none', 'important');
                        }
                    }
                    return panes.some((pane) => {
                        const box = pane.getBoundingClientRect();
                        return box.width > 0 && box.height > 0;
                    });
                }"""
            ) or has_visible_pane
        if not has_visible_pane:
            closed_polls += 1
            if closed_polls >= 3:
                return
        else:
            closed_polls = 0
        page.wait_for_timeout(100)
    raise AssertionError("Could not close Calendar settings side pane")


def _wait_for_button_disabled(button) -> None:
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    while datetime.now().timestamp() < deadline:
        if not button.is_enabled():
            return
        button.page.wait_for_timeout(100)
    raise AssertionError("Button did not become disabled after save")


def add_blocked_time(page: Page, params: dict[str, str]) -> None:
    _remove_open_angular_dialogs(page)
    _, vue = navigate_calendar(page, params["display"], params.get("navigate_to"))
    _remove_open_angular_dialogs(page)
    if params.get("timeslot_end") and not _try_choose_calendar_range(page, vue, params):
        _, vue = navigate_calendar(page, params["display"], params.get("navigate_to"))
        _remove_open_angular_dialogs(page)
        choose_calendar_slot(vue, params["display"], params["timeslot"])
    elif not params.get("timeslot_end"):
        choose_calendar_slot(vue, params["display"], params["timeslot"])
    vue.locator('[data-qa="option-block_off_time"]').click(timeout=UI_TIMEOUT)
    dialog = vue.locator('[data-qa="did-mount"]').first
    dialog.wait_for(state="visible", timeout=UI_TIMEOUT)
    if params.get("timeslot_end"):
        _select_time(vue, "service-end-time-input", _inclusive_slot_end_time(params["timeslot_end"]))
    if params.get("title"):
        title_input = vue.locator('.custom-title-input [data-qa="vc-text-field"]').first
        title_input.fill(params["title"])
    if params.get("additional_staffs"):
        vue.locator(".staff-picker-button").click(timeout=UI_TIMEOUT)
        active_staff_menu = vue.locator(".menuable__content__active").last
        for staff in params["additional_staffs"].split(","):
            _click_staff_picker_option(active_staff_menu, staff.strip())
        vue.locator(".staff-picker-button").click(timeout=UI_TIMEOUT)
    submit_button = vue.locator(".submit-button").first
    submit_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    submit_button.evaluate("(button) => button.click()")
    _wait_for_dialog_to_close(vue)


def _click_staff_picker_option(active_staff_menu, staff_name: str) -> None:
    clicked = active_staff_menu.evaluate(
        """(menu, staffName) => {
            const rows = Array.from(menu.querySelectorAll('.v-list-item, .vc-checkbox, label, div'));
            const row = rows.find((candidate) => {
                const text = (candidate.innerText || candidate.textContent || '').replace(/\\s+/g, ' ').trim();
                const box = candidate.getBoundingClientRect();
                return box.width > 0 && box.height > 0 && text === staffName;
            });
            if (!row) return false;
            const target = row.closest('.v-list-item, .vc-checkbox, label') || row;
            target.click();
            return true;
        }""",
        staff_name,
    )
    if not clicked:
        active_staff_menu.get_by_text(staff_name, exact=True).click(force=True, timeout=UI_TIMEOUT)


def _try_choose_calendar_range(page: Page, vue, params: dict[str, str]) -> bool:
    try:
        choose_calendar_slot(vue, params["display"], params["timeslot"], params["timeslot_end"])
        return True
    except PlaywrightTimeoutError:
        _remove_open_angular_dialogs(page)
        open_calendar_page(page)
        return False


def drag_calendar_item(page: Page, title: str, display: str, direction: str, new_timeslot: str) -> None:
    _, vue = navigate_calendar(page, display, direction)
    _remove_open_angular_dialogs(page)
    item = _draggable_calendar_item(vue, title)
    target = _slot_locator(vue, display, new_timeslot)
    item.wait_for(state="visible", timeout=UI_TIMEOUT)
    target.wait_for(state="visible", timeout=UI_TIMEOUT)
    _reschedule_item_through_calendar_action(vue, title, display, direction, new_timeslot)
    _remove_open_angular_dialogs(page)
    page.reload(wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    open_calendar_page(page)


def _draggable_calendar_item(vue, title: str):
    candidates = vue.locator(".smart-scheduler-event-content.vc-event").filter(has_text=title)
    count = candidates.count()
    if count == 0:
        return candidates.first

    for index in range(count):
        candidate = candidates.nth(index)
        draggable_state = candidate.evaluate(
            """node => {
                const eventNode = node.closest('.smart-scheduler-event');
                const data = eventNode?._item || eventNode?.item || eventNode?.dataItem || {};
                return {
                    draggableAttr: eventNode?.getAttribute('draggable'),
                    readOnly: Boolean(data.readOnly || data.isReadOnly),
                    draggable: data.draggable,
                    subjectType: data.subject_type,
                };
            }"""
        )
        if draggable_state.get("draggableAttr") == "true" and not draggable_state.get("readOnly") and draggable_state.get("draggable") is not False:
            return candidate
    return candidates.first


def _remove_open_angular_dialogs(page: Page) -> None:
    for frame in page.frames:
        frame.evaluate(
            """() => {
                try {
                    const angularEl = window.angular?.element?.(document.body);
                    const injector = angularEl?.injector?.();
                    injector?.get?.('$mdDialog')?.cancel?.();
                } catch (_) {}
                const textMatches = Array.from(document.querySelectorAll('body *'))
                    .filter((node) => (node.innerText || '').includes('Propose a new time'))
                    .sort((a, b) => (a.innerText || '').length - (b.innerText || '').length);
                for (const match of textMatches) {
                    const dialog = match.closest('[role="dialog"], md-dialog, .md-dialog-container, .modal-dialog, .modal');
                    (dialog || match).remove();
                }
                for (const node of Array.from(document.querySelectorAll('md-dialog, md-backdrop, .md-dialog-container, .md-scroll-mask, .modal-backdrop'))) {
                    node.remove();
                }
            }"""
        )


def _reschedule_item_through_calendar_action(vue, title: str, display: str, direction: str, new_timeslot: str) -> datetime:
    target = _timeslot_datetime(display, direction, new_timeslot)
    if target is None:
        raise AssertionError(f"Could not resolve target timeslot {new_timeslot}")
    vue.evaluate(
        """({ title, targetIso }) => {
            const scheduler = document.querySelector('smart-scheduler');
            const sourceItems = Array.from(scheduler?.dataSource || []);
            const item = sourceItems.find((candidate) => {
                if (candidate.subject_type !== 'BlockedTime') return false;
                const searchable = [
                    candidate.label,
                    candidate.title,
                    candidate.subject?.title,
                    candidate.subject?.name,
                ].filter(Boolean).join(' ');
                return searchable.includes(title);
            });
            if (!item) throw new Error(`Could not find calendar item ${title} in scheduler dataSource`);

            const dateStart = new Date(targetIso);
            const duration = new Date(item.dateEnd).getTime() - new Date(item.dateStart).getTime();
            const dateEnd = new Date(dateStart.getTime() + duration);
            const movedItem = { ...item, dateStart, dateEnd };
            window.parent.postMessage({
                event: 'vue-message',
                origin: new URLSearchParams(window.location.search).get('iframeId'),
                data: {
                    eventName: 'calendar-action',
                    data: { action: 'reschedule_item', data: { item: movedItem } },
                },
            }, '*');
        }""",
        {"title": title, "targetIso": target.strftime("%Y-%m-%dT%H:%M:%S")},
    )
    return target


def _wait_for_scheduler_item_start(page: Page, vue, title: str, target: datetime) -> None:
    target_parts = {
        "year": target.year,
        "month": target.month - 1,
        "day": target.day,
        "hour": target.hour,
        "minute": target.minute,
    }
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    scheduler = vue.locator("smart-scheduler").first
    last_start = ""

    while datetime.now().timestamp() < deadline:
        _remove_open_angular_dialogs(page)
        last_start = scheduler.evaluate(
            """(node, { title, target }) => {
                const item = Array.from(node.dataSource || []).find((candidate) => {
                    if (candidate.subject_type !== 'BlockedTime') return false;
                    const searchable = [
                        candidate.label,
                        candidate.title,
                        candidate.subject?.title,
                        candidate.subject?.name,
                    ].filter(Boolean).join(' ');
                    return searchable.includes(title);
                });
                if (!item?.dateStart) return '';
                const start = new Date(item.dateStart);
                const matches =
                    start.getFullYear() === target.year &&
                    start.getMonth() === target.month &&
                    start.getDate() === target.day &&
                    start.getHours() === target.hour &&
                    start.getMinutes() === target.minute;
                return matches ? 'MATCH' : start.toString();
            }""",
            {"title": title, "target": target_parts},
        )
        if last_start == "MATCH":
            return
        vue.page.wait_for_timeout(100)

    raise AssertionError(f"Calendar item {title} did not move to {target}. Last start: {last_start}")


def edit_blocked_time(page: Page, old_title: str, new_title: str, new_start_time: str) -> None:
    search_title = old_title
    duration_minutes = None
    for attempt in range(2):
        _, vue = get_calendar_frames(page)
        item = _blocked_time_item(vue, search_title)
        duration_minutes = duration_minutes or _blocked_time_duration_minutes(item)
        _edit_blocked_time_dialog(vue, item, new_title, new_start_time, duration_minutes)
        if _wait_for_blocked_time_update(page, vue, new_title, new_start_time, duration_minutes):
            return
        search_title = new_title
    raise AssertionError(f"Blocked time did not update to {new_title} at {new_start_time}")


def _edit_blocked_time_dialog(vue, item, new_title: str, new_start_time: str, duration_minutes: int | None) -> None:
    item.click(timeout=UI_TIMEOUT)
    dialog = vue.locator('[data-qa="did-mount"]').first
    dialog.wait_for(state="visible", timeout=UI_TIMEOUT)
    vue.locator('.custom-title-input [data-qa="vc-text-field"]').fill(new_title)
    _select_time_with_verification(vue, "service-start-time-input", new_start_time)
    if duration_minutes:
        _select_time_with_verification(vue, "service-end-time-input", _time_after(new_start_time, duration_minutes))
    vue.locator(".submit-button").click(timeout=UI_TIMEOUT)
    _wait_for_dialog_to_close(vue)


def _wait_for_blocked_time_update(page: Page, vue, title: str, start_time: str, duration_minutes: int | None) -> bool:
    target = datetime.strptime(start_time.upper(), "%I:%M %p")
    expected_duration = duration_minutes or 0
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    scheduler = vue.locator("smart-scheduler").first
    while datetime.now().timestamp() < deadline:
        result = scheduler.evaluate(
            """(node, { title, hour, minute, duration }) => {
                const item = Array.from(node.dataSource || []).find((candidate) => {
                    if (candidate.subject_type !== 'BlockedTime') return false;
                    const searchable = [
                        candidate.label,
                        candidate.title,
                        candidate.subject?.title,
                        candidate.subject?.name,
                    ].filter(Boolean).join(' ');
                    return searchable.includes(title);
                });
                if (!item?.dateStart || !item?.dateEnd) return 'missing';
                const start = new Date(item.dateStart);
                const actualDuration = Math.round((new Date(item.dateEnd).getTime() - start.getTime()) / 60000);
                if (start.getHours() === hour && start.getMinutes() === minute && (!duration || actualDuration === duration)) {
                    return 'MATCH';
                }
                return `${start.toTimeString()} duration=${actualDuration}`;
            }""",
            {"title": title, "hour": target.hour, "minute": target.minute, "duration": expected_duration},
        )
        if result == "MATCH":
            return True
        page.wait_for_timeout(150)
    return False


def _blocked_time_duration_minutes(item) -> int | None:
    return item.evaluate(
        """(node) => {
            const eventNode = node.closest('.smart-scheduler-event');
            const data = eventNode?._item || eventNode?.item || eventNode?.dataItem || {};
            if (!data.dateStart || !data.dateEnd) return null;
            return Math.round((new Date(data.dateEnd).getTime() - new Date(data.dateStart).getTime()) / 60000);
        }"""
    )


def _time_after(start_time: str, duration_minutes: int) -> str:
    start = datetime.strptime(start_time.upper(), "%I:%M %p")
    end = start + timedelta(minutes=duration_minutes)
    return end.strftime("%I:%M %p")


def _blocked_time_item(vue, title: str):
    candidates = vue.locator(".smart-scheduler-event-content.vc-event")
    for index in range(candidates.count()):
        candidate = candidates.nth(index)
        matches = candidate.evaluate(
            """(node, title) => {
                const eventNode = node.closest('.smart-scheduler-event');
                const data = eventNode?._item || eventNode?.item || eventNode?.dataItem || {};
                if (data.subject_type !== 'BlockedTime') return false;
                const searchable = [
                    data.label,
                    data.title,
                    data.subject?.title,
                    data.subject?.name,
                    node.textContent,
                ].filter(Boolean).join(' ');
                return searchable.includes(title);
            }""",
            title,
        )
        if matches:
            return candidate
    return candidates.filter(has_text=title).first


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


def assert_calendar_items(page: Page, direction: str, display: str, expected: list[dict[str, str]], exact: bool = False) -> None:
    _, vue = navigate_calendar(page, display, direction)
    _scroll_scheduler_to_expected_items(vue, display, expected)
    last_items: list[dict[str, Any]] = []
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    while datetime.now().timestamp() < deadline:
        last_items = parse_calendar_items(vue, display)
        if _items_match(last_items, expected, exact=exact):
            return
        page.wait_for_timeout(500)
    raise AssertionError(f"Calendar items did not match.\nExpected: {expected}\nActual: {last_items}")


def _scroll_scheduler_to_expected_items(vue, display: str, expected: list[dict[str, str]]) -> None:
    if display not in {"3 Days", "Week", "Day"}:
        return
    start_time = _earliest_expected_start_time(expected)
    if not start_time:
        return
    _scroll_scheduler_to_slot(vue, display, f"monday,{start_time}")
    wait_for_calendar_idle(vue)


def _earliest_expected_start_time(expected: list[dict[str, str]]) -> str | None:
    starts = []
    for item in expected:
        item_times = item.get("item_times", "")
        start = _parse_item_start_time(item_times)
        if start:
            starts.append(start)
    if not starts:
        return None
    earliest = min(starts)
    return earliest.strftime("%I:%M %p").lower().lstrip("0")


def _parse_item_start_time(item_times: str) -> datetime | None:
    match = re.match(r"(?P<start>\d{1,2}(?::\d{2})?)\s*-\s*(?P<end>\d{1,2}(?::\d{2})?)(?P<period>am|pm)$", item_times)
    if not match:
        return None
    start_text = match.group("start")
    period = match.group("period")
    if ":" not in start_text:
        start_text = f"{start_text}:00"
    try:
        return datetime.strptime(f"{start_text}{period}", "%I:%M%p")
    except ValueError:
        return None


def assert_calendar_items_absent(page: Page, direction: str, display: str, unexpected: list[dict[str, str]]) -> None:
    _, vue = navigate_calendar(page, display, direction)
    items = parse_calendar_items(vue, display)
    for unexpected_item in unexpected:
        if _find_matching_item(items, unexpected_item, set()) is not None:
            raise AssertionError(f"Unexpected calendar item was visible.\nUnexpected: {unexpected_item}\nActual: {items}")


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


def switch_logged_in_staff(page: Page, context: dict, staff: dict) -> None:
    token = get_sso_token(context, staff)
    base_url = resolve_partner_base_url(context)
    redirect_to = quote("/app/dashboard", safe="")
    try:
        page.goto(
            f"{base_url}/v1/partners/sso/login?staff_uid={staff_uid(staff)}&sso_token={token}&redirect_to={redirect_to}",
            wait_until="domcontentloaded",
            timeout=UI_TIMEOUT,
        )
    except PlaywrightError as error:
        if "ERR_ABORTED" not in str(error):
            raise
    page.wait_for_url("**/app/dashboard**", timeout=UI_TIMEOUT)


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
    _scroll_scheduler_to_slot(vue, display, timeslot)
    slot = _slot_locator(vue, display, timeslot)
    slot.scroll_into_view_if_needed(timeout=UI_TIMEOUT)
    slot.wait_for(state="visible", timeout=UI_TIMEOUT)
    if not timeslot_end:
        slot.click(timeout=UI_TIMEOUT)
    else:
        _scroll_scheduler_to_slot(vue, display, timeslot_end)
        end_slot = _slot_locator(vue, display, timeslot_end)
        end_slot.scroll_into_view_if_needed(timeout=UI_TIMEOUT)
        end_slot.wait_for(state="visible", timeout=UI_TIMEOUT)
        _drag_slot_range(vue, slot, end_slot)
        if _active_cell_action_menu_visible(vue, timeout=1_000):
            return
        _remove_open_angular_dialogs(vue.page)
        slot.click(timeout=UI_TIMEOUT)
    vue.locator(".v-menu__content.menuable__content__active").wait_for(state="visible", timeout=UI_TIMEOUT)


def _active_cell_action_menu_visible(vue, timeout: int = UI_TIMEOUT) -> bool:
    try:
        vue.locator(".v-menu__content.menuable__content__active").wait_for(state="visible", timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        return False


def _drag_slot_range(vue, start_slot, end_slot) -> None:
    start_slot.hover(timeout=UI_TIMEOUT)
    vue.page.wait_for_timeout(100)
    start_box = start_slot.bounding_box(timeout=UI_TIMEOUT)
    end_box = end_slot.bounding_box(timeout=UI_TIMEOUT)
    if not start_box or not end_box:
        raise AssertionError("Could not resolve calendar slot drag coordinates")
    mouse = vue.page.mouse
    start_x = start_box["x"] + start_box["width"] / 2
    start_y = start_box["y"] + start_box["height"] / 2
    end_x = end_box["x"] + end_box["width"] / 2
    end_y = end_box["y"] + end_box["height"] / 2
    mouse.move(start_x, start_y)
    mouse.down()
    mouse.move(end_x, end_y, steps=12)
    mouse.up()


def _scroll_scheduler_to_slot(vue, display: str, timeslot: str) -> None:
    if display not in {"3 Days", "Week", "Day"}:
        return
    time_text = timeslot.split(",", 1)[1].strip() if "," in timeslot else timeslot.strip()
    try:
        target_time = datetime.strptime(time_text.upper(), "%I:%M %p")
    except ValueError:
        return
    vue.locator("smart-scheduler").first.evaluate(
        """(scheduler, { hour, minute }) => {
            const view = scheduler.querySelector('.smart-scheduler-view');
            if (!view) return;
            const dayHeight = view.scrollHeight;
            const ratio = (hour + minute / 60) / 24;
            view.scrollTop = Math.max(0, (dayHeight * ratio) - 120);
        }""",
        {"hour": target_time.hour, "minute": target_time.minute},
    )


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
                const state = classes.includes('client-approval') ? 'invited' : node.getAttribute('data-state') || '';
                return {
                    item_type: itemType,
                    state,
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
        return vue.locator(f'.smart-scheduler-cell[data-qa="{timeslot}"]').first
    if display == "3 Days":
        column, hour = [part.strip() for part in timeslot.split(",", 1)]
        return vue.locator(f'.smart-scheduler-cell[data-qa*="{hour}"]').nth(THREE_DAY_COLUMN[column])
    if display == "Day" and timeslot == "all_day":
        return vue.locator('.smart-scheduler-cell[data-all-day="true"]').first
    return vue.locator(f'.smart-scheduler-cell[data-qa*="{timeslot}"]').first


def _select_client(angular, client_name: str) -> None:
    search = angular.get_by_role("textbox", name="Search by name, email or tag")
    search.wait_for(state="visible", timeout=UI_TIMEOUT)
    result = angular.get_by_role("button").filter(has_text=client_name).first
    for attempt in range(2):
        search.fill("")
        search.press_sequentially(client_name, delay=25)
        try:
            result.wait_for(state="visible", timeout=UI_TIMEOUT)
            result.click(timeout=UI_TIMEOUT)
            return
        except PlaywrightTimeoutError:
            if attempt == 1:
                raise


def _set_appointment_fields(vue, params: dict[str, str], context: dict, slot_date: datetime | None = None) -> None:
    if params.get("assigned_staff"):
        _choose_select_option(vue, vue.locator(".staff-selection").first, params["assigned_staff"])
    if params.get("meeting_date"):
        _select_relative_date(vue, params["meeting_date"], slot_date)
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
    field = vue.locator(f'[data-qa="{data_qa}"]').first
    field.click(timeout=UI_TIMEOUT)
    if _click_time_option(vue, time_text):
        return
    option = vue.locator(f'div.menuable__content__active div button[data-qa="item-{time_text}"]').first
    option.click(timeout=UI_TIMEOUT)


def _click_time_option(vue, time_text: str) -> bool:
    alternatives = [time_text]
    if time_text.startswith("0"):
        alternatives.append(time_text[1:])
    return vue.evaluate(
        """(timeTexts) => {
            const activeMenus = Array.from(document.querySelectorAll('.menuable__content__active'));
            const buttons = activeMenus.flatMap((menu) => Array.from(menu.querySelectorAll('button')));
            const option = buttons.find((button) => {
                const box = button.getBoundingClientRect();
                const text = (button.innerText || button.textContent || '').replace(/\\s+/g, ' ').trim();
                const dataQa = button.getAttribute('data-qa') || '';
                return box.width > 0 && box.height > 0 && timeTexts.some((timeText) => {
                    return dataQa === `item-${timeText}` || text === timeText;
                });
            });
            if (!option) return false;
            option.scrollIntoView({ block: 'center', inline: 'center' });
            for (const eventName of ['pointerdown', 'mousedown', 'pointerup', 'mouseup']) {
                option.dispatchEvent(new MouseEvent(eventName, { bubbles: true, cancelable: true, view: window }));
            }
            option.click();
            return true;
        }""",
        alternatives,
    )


def _select_time_with_verification(vue, data_qa: str, time_text: str) -> None:
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    last_value = ""
    while datetime.now().timestamp() < deadline:
        _select_time(vue, data_qa, time_text)
        last_value = _time_field_value(vue, data_qa)
        if _time_value_matches(last_value, time_text):
            return
        vue.page.wait_for_timeout(150)
    raise AssertionError(f"Time field {data_qa} did not change to {time_text}. Last value: {last_value}")


def _time_field_value(vue, data_qa: str) -> str:
    return vue.locator(f'[data-qa="{data_qa}"]').first.evaluate(
        """(field) => {
            const input = field.querySelector('input');
            return [input?.value, field.innerText, field.textContent].filter(Boolean).join(' ');
        }"""
    )


def _time_value_matches(actual: str, expected: str) -> bool:
    normalized_actual = re.sub(r"\s+", "", actual).lower()
    normalized_expected = re.sub(r"^0", "", re.sub(r"\s+", "", expected).lower())
    return normalized_expected in normalized_actual or re.sub(r"^0", "", normalized_expected) in normalized_actual


def _select_relative_date(vue, date_key: str, slot_date: datetime | None = None) -> None:
    if not date_key:
        return
    offsets = {"next_week": 7, "last_week": -7, "next_day": 1, "last_day": -1}
    if date_key not in offsets:
        return
    date_input = vue.locator('[data-qa="date-picker-text-input"]:visible').first
    target = (slot_date or datetime.now()) + timedelta(days=offsets[date_key])
    target_day = target.day
    date_input.click(timeout=UI_TIMEOUT)
    vue.locator(".date-picker-menu-content button").filter(has_text=str(target_day)).last.click(timeout=UI_TIMEOUT)


def _slot_date(display: str, direction: str, timeslot: str) -> datetime | None:
    if display.lower() not in {"week", "3 days"}:
        return None
    day_name = timeslot.split(",", 1)[0].strip().lower()
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    if day_name not in weekdays:
        return None
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    if direction == "next":
        week_start += timedelta(days=7)
    elif direction == "previous":
        week_start -= timedelta(days=7)
    return week_start + timedelta(days=weekdays[day_name])


def _timeslot_datetime(display: str, direction: str, timeslot: str) -> datetime | None:
    target_date = _slot_date(display, direction, timeslot)
    if target_date is None:
        return None
    _, time_text = [part.strip() for part in timeslot.split(",", 1)]
    parsed_time = datetime.strptime(time_text.upper(), "%I:%M %p")
    return target_date.replace(hour=parsed_time.hour, minute=parsed_time.minute, second=0, microsecond=0)


def _inclusive_slot_end_time(timeslot: str) -> str:
    time_text = timeslot.split(",", 1)[1].strip() if "," in timeslot else timeslot.strip()
    end_time = datetime.strptime(time_text.upper(), "%I:%M %p") + timedelta(minutes=30)
    return end_time.strftime("%I:%M %p")


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
    dialog = vue.get_by_role("dialog").first
    if _wait_for_dialog_hidden(dialog):
        return
    wait_for_calendar_idle(vue)
    if not _wait_for_dialog_hidden(dialog):
        raise AssertionError("Dialog did not close after submit")


def _wait_for_appointment_submit(vue, params: dict[str, str]) -> None:
    dialog = vue.get_by_role("dialog").first
    if _wait_for_dialog_hidden_after_submit(vue, dialog):
        return
    created_in_past = params.get("navigate_to") == "previous" or params.get("meeting_date") in {"last_week", "last_day"}
    requires_confirmation = params.get("client_confirmation") == "Checked"
    if not created_in_past and not requires_confirmation:
        _close_active_dialog(vue, dialog)
        return
    _close_active_dialog(vue, dialog)


def _wait_for_dialog_hidden_after_submit(vue, dialog) -> bool:
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    while datetime.now().timestamp() < deadline:
        try:
            dialog.wait_for(state="hidden", timeout=500)
            return True
        except PlaywrightTimeoutError:
            _click_visible_appointment_submit(vue, fail_if_missing=False)
    return False


def _wait_for_dialog_hidden(dialog) -> bool:
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    while datetime.now().timestamp() < deadline:
        try:
            dialog.wait_for(state="hidden", timeout=500)
            return True
        except PlaywrightTimeoutError:
            continue
    return False


def _click_visible_appointment_submit(vue, fail_if_missing: bool = True) -> bool:
    if _click_visible_appointment_submit_by_js(vue):
        return True
    button = vue.locator("button:visible").filter(has_text=re.compile(r"Schedule\s*appointment|^Schedule$", re.I)).last
    clicked = False
    try:
        button.wait_for(state="visible", timeout=1_000)
        if button.is_enabled():
            button.click(force=True, timeout=1_000)
            clicked = True
    except PlaywrightTimeoutError:
        pass

    if _click_visible_appointment_submit_by_js(vue):
        return True
    if clicked:
        return True
    if fail_if_missing:
        raise AssertionError("Could not find visible Schedule appointment button")
    return False


def _click_visible_appointment_submit_by_js(vue) -> bool:
    click_script = """() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const matches = buttons.filter((candidate) => {
            const text = (candidate.innerText || candidate.textContent || '').replace(/\\s+/g, ' ').trim();
            const box = candidate.getBoundingClientRect();
            return /Schedule\\s*appointment|^Schedule$/i.test(text) &&
                !candidate.disabled &&
                candidate.getAttribute('aria-disabled') !== 'true' &&
                box.width > 0 &&
                box.height > 0;
        });
        const button = matches.at(-1);
        if (!button) return false;
        button.scrollIntoView({ block: 'center', inline: 'center' });
        button.focus();
        for (const eventName of ['pointerdown', 'mousedown', 'pointerup', 'mouseup']) {
            button.dispatchEvent(new MouseEvent(eventName, { bubbles: true, cancelable: true, view: window }));
        }
        button.click();
        return true;
    }"""
    return any(frame.evaluate(click_script) for frame in vue.page.frames)


def _wait_and_click_visible_appointment_submit(vue) -> None:
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    while datetime.now().timestamp() < deadline:
        if _click_visible_appointment_submit(vue, fail_if_missing=False):
            return
        vue.page.wait_for_timeout(100)
    raise AssertionError("Could not find visible Schedule appointment button")


def _close_active_dialog(vue, dialog) -> None:
    if not dialog.is_visible():
        return
    vue.locator("body").press("Escape")
    try:
        dialog.wait_for(state="hidden", timeout=1_000)
        return
    except PlaywrightTimeoutError:
        pass
    if _click_dialog_close_control(vue):
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


def _click_dialog_close_control(vue) -> bool:
    click_script = """() => {
        const controls = Array.from(document.querySelectorAll('button, .v-icon, .icon-close_new'));
        const control = controls.find((candidate) => {
            const text = (candidate.innerText || candidate.textContent || '').replace(/\\s+/g, ' ').trim();
            const classes = candidate.className || '';
            const box = candidate.getBoundingClientRect();
            return box.width > 0 &&
                box.height > 0 &&
                (/^Cancel$/i.test(text) || String(classes).includes('icon-close_new') || String(classes).includes('mdi-close'));
        });
        if (!control) return false;
        control.click();
        return true;
    }"""
    return any(frame.evaluate(click_script) for frame in vue.page.frames)


def _items_match(actual: list[dict[str, str]], expected: list[dict[str, str]], exact: bool = False) -> bool:
    if len(actual) < len(expected):
        return False
    used_indexes: set[int] = set()
    for expected_item in expected:
        match_index = _find_matching_item(actual, expected_item, used_indexes)
        if match_index is None:
            return False
        used_indexes.add(match_index)
    if exact and len(used_indexes) != len(actual):
        return False
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
