"""UI helpers for the multistaff migration (VCITA2-13950).

The BO appointment dialog is a Vue app (`#vue_iframe_layout`) nested in the Angular
frontage iframe (`iframe[title="angularjs"]`); the appointment meeting page renders in the
Angular iframe. Selectors are reused from the proven `create_appointment` flow and from the
legacy page objects (createMeetingDialog.js / appointment.js) and verified against current
frontage source (StaffSelection.vue, additionalStaff(Popover).vue, appointment-t.html.haml).
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from tests.scheduling.appointments.appointment_helpers import UI_TIMEOUT, open_calendar_page
from tests.scheduling.appointments.multistaff.multistaff_api import list_appointment_ids

_SETTLE_MS = 250


def _frames(page: Page):
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator("#vue_iframe_layout")
    return outer, inner


def _app_base(page: Page) -> str:
    if "/app/" not in page.url:
        raise ValueError(f"Cannot infer app base URL from: {page.url}")
    return page.url.split("/app/")[0]


def _schedule_button(inner):
    return inner.get_by_role("button", name=re.compile(r"Schedule\s*appointment", re.I)).or_(
        inner.get_by_role("button", name=re.compile(r"^Schedule$", re.I))
    ).first


def schedule_appointment(
    page: Page, context: dict, client_name: str, service_name: str,
    additional_staff: list[str] | None = None,
) -> str:
    """Schedule an appointment via the BO calendar dialog and return the new appointment id.

    The id is resolved by snapshotting the business appointments before/after (legacy
    addBookingToContext picked the booking not yet seen). ``additional_staff`` (display
    names) are selected through the additional-staff picker before submitting.
    """
    before_ids = list_appointment_ids(context)
    open_calendar_page(page)
    outer, inner = _frames(page)

    _open_new_appointment(page, outer, inner, client_name)
    _pick_service(page, inner, service_name)

    _schedule_button(inner).wait_for(state="visible", timeout=UI_TIMEOUT)
    _set_tomorrow_10am(inner)
    _fill_address_if_present(page, inner)
    if additional_staff:
        _select_additional_staff(page, inner, additional_staff)

    submit = _schedule_button(inner)
    submit.wait_for(state="visible", timeout=UI_TIMEOUT)
    submit.click(force=True)
    return _wait_for_new_appointment(page, context, before_ids)


def _open_new_appointment(page: Page, outer, inner, client_name: str) -> None:
    last_error: Exception | None = None
    for attempt in range(2):
        new_btn = inner.get_by_role("button", name="New")
        new_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
        new_btn.click()
        appointment_option = inner.get_by_role("menuitem", name="Appointment", exact=True)
        appointment_option.wait_for(state="visible", timeout=UI_TIMEOUT)
        appointment_option.click(timeout=UI_TIMEOUT)
        outer.get_by_role("dialog").wait_for(state="visible", timeout=UI_TIMEOUT)

        search = outer.get_by_role("textbox", name="Search by name, email or tag")
        search.click(timeout=UI_TIMEOUT)
        page.wait_for_timeout(100)
        search.press_sequentially(client_name, delay=30)
        client_option = outer.get_by_role("button").filter(has_text=client_name)
        client_option.wait_for(state="visible", timeout=UI_TIMEOUT)
        client_option.click(timeout=UI_TIMEOUT)

        service_picker = inner.locator('[data-qa="service-picker-modal"]:visible')
        try:
            service_picker.wait_for(state="visible", timeout=UI_TIMEOUT)
            return
        except PlaywrightTimeoutError as exc:
            last_error = exc
    raise last_error or AssertionError("Service picker did not open after client selection")


def _pick_service(page: Page, inner, service_name: str) -> None:
    service_picker = inner.locator('[data-qa="service-picker-modal"]:visible')
    search = service_picker.get_by_role("searchbox", name="Search")
    search.click(timeout=UI_TIMEOUT)
    page.wait_for_timeout(100)
    search.press_sequentially(service_name, delay=30)
    service_row = service_picker.locator(".service-item").filter(has_text=service_name).first
    service_row.wait_for(state="visible", timeout=UI_TIMEOUT)
    service_row.locator('[data-qa="service-name"]').click(timeout=UI_TIMEOUT)
    service_picker.wait_for(state="hidden", timeout=UI_TIMEOUT)


def _set_tomorrow_10am(inner) -> None:
    try:
        tomorrow = datetime.now() + timedelta(days=1)
        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().year
        date_field = inner.get_by_text(
            re.compile(rf"\d{{1,2}}\s+{current_month}\s+{current_year}")
        ).first
        date_field.click(timeout=UI_TIMEOUT)
        inner.get_by_role("button", name=str(tomorrow.day)).last.click(timeout=UI_TIMEOUT)
    except Exception:  # noqa: BLE001 - default (near-future) date is acceptable
        pass
    try:
        start = inner.locator('[data-qa="service-start-time-input"] input').first
        start.click(timeout=UI_TIMEOUT)
        inner.locator('[data-qa="item-10:00 AM"]').first.click(timeout=UI_TIMEOUT)
    except Exception:  # noqa: BLE001 - default start time is acceptable
        pass


def _fill_address_if_present(page: Page, inner) -> None:
    address = inner.get_by_role("textbox", name=re.compile(r"Address", re.I)).first
    if address.count() > 0:
        address.click()
        address.press_sequentially("123 Test Street", delay=30)
        page.wait_for_timeout(300)
        page.keyboard.press("Tab")
        page.wait_for_timeout(500)


def _select_additional_staff(page: Page, inner, names: list[str]) -> None:
    button = inner.locator(".additional-staff__button")
    button.wait_for(state="visible", timeout=UI_TIMEOUT)
    button.click(timeout=UI_TIMEOUT)
    inner.locator('[data-qa="additional-staff-listbox"]').wait_for(state="visible", timeout=UI_TIMEOUT)
    for name in names:
        _set_listbox_item(page, inner, name, checked=True)
    done = inner.locator('[data-qa="vc-footer-Done"]')
    done.wait_for(state="visible", timeout=UI_TIMEOUT)
    done.click(timeout=UI_TIMEOUT)


def _listbox_row(scope, name: str):
    row = scope.locator(f'[data-qa="additional-staff-listbox-{name}"]')
    if row.count() > 0:
        return row.first
    return scope.locator('[data-qa="additional-staff-listbox"] .v-list-item').filter(has_text=name).first


def _set_listbox_item(page: Page, scope, name: str, *, checked: bool) -> None:
    row = _listbox_row(scope, name)
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    for _ in range(3):
        if _row_checked(row) == checked:
            return
        row.click(timeout=UI_TIMEOUT)
        page.wait_for_timeout(150)
    if _row_checked(row) != checked:
        raise AssertionError(f"Could not set additional staff {name!r} checked={checked}")


def _row_checked(row) -> bool:
    checkbox = row.locator("input").first
    aria = checkbox.get_attribute("aria-checked")
    if aria is not None:
        return aria == "true"
    try:
        return checkbox.is_checked()
    except Exception:  # noqa: BLE001
        return False


_NEW_APPOINTMENT_BUDGET_MS = 10_000  # bounded poll; the legacy flow waited up to 15s for
# the created booking to surface (UI create + API propagation), so a 10s read-back poll is
# justified and still tighter than legacy.


def _wait_for_new_appointment(page: Page, context: dict, before_ids: set[str]) -> str:
    for _ in range(int(_NEW_APPOINTMENT_BUDGET_MS / _SETTLE_MS)):
        new_ids = list_appointment_ids(context) - before_ids
        if new_ids:
            return next(iter(new_ids))
        page.wait_for_timeout(_SETTLE_MS)
    raise AssertionError("New appointment was not created (no new id appeared in the bookings read-back)")


def open_meeting_page(page: Page, appointment_id: str):
    """Navigate to the appointment meeting page and return the Angular frame locator."""
    page.goto(
        f"{_app_base(page)}/app/appointments/{appointment_id}",
        wait_until="domcontentloaded",
        timeout=UI_TIMEOUT,
    )
    page.wait_for_selector('iframe[title="angularjs"]', state="visible", timeout=UI_TIMEOUT)
    outer = page.frame_locator('iframe[title="angularjs"]')
    outer.locator("div.summary-header h3").wait_for(state="visible", timeout=UI_TIMEOUT)
    return outer


def meeting_text(outer, data_qa: str) -> str:
    locator = outer.locator(f'[data-qa="{data_qa}"]')
    if locator.count() == 0:
        return ""
    return (locator.first.inner_text() or "").strip()


def meeting_name(outer) -> str:
    return (outer.locator("div.summary-header h3").first.inner_text() or "").strip()


def remove_additional_staff(page: Page, name: str) -> None:
    """Remove an additional staff from the open meeting page (edit -> uncheck -> Done)."""
    outer = page.frame_locator('iframe[title="angularjs"]')
    edit_link = outer.locator("[data-qa='assigned-additional-staff'] a")
    edit_link.wait_for(state="visible", timeout=UI_TIMEOUT)
    edit_link.click(timeout=UI_TIMEOUT)

    dialog = _dialog_frame(page)
    _set_listbox_item(page, dialog, name, checked=False)
    done = dialog.locator('[data-qa="vc-footer-Done"]')
    done.wait_for(state="visible", timeout=UI_TIMEOUT)
    done.click(timeout=UI_TIMEOUT)
    _wait_overlay_closed(page)


def _dialog_frame(page: Page):
    for _ in range(int(UI_TIMEOUT / _SETTLE_MS)):
        for frame in page.frames:
            try:
                if frame.locator('[data-qa="vc-footer-Done"]').count() > 0:
                    return frame
            except Exception:  # noqa: BLE001 - frame may be navigating
                continue
        page.wait_for_timeout(_SETTLE_MS)
    raise AssertionError("Additional-staff edit dialog (Done button) did not appear")


def _wait_overlay_closed(page: Page) -> None:
    for _ in range(int(UI_TIMEOUT / _SETTLE_MS)):
        still_open = any(
            _safe_count(frame, ".v-overlay--active") > 0 for frame in page.frames
        )
        if not still_open:
            return
        page.wait_for_timeout(_SETTLE_MS)


def _safe_count(frame, selector: str) -> int:
    try:
        return frame.locator(selector).count()
    except Exception:  # noqa: BLE001
        return 0
