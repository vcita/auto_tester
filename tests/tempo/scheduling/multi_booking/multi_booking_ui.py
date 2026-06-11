"""UI helpers for the multi-booking subcategory.

Covers the back-office linked (multi-service) appointment flow that the legacy
automation-js multi-booking-appointments.feature exercises: scheduling a single
appointment composed of several services via the calendar New dialog, opening a
back-office appointment by id, reading its state / price / linked-booking
description, cancelling a single or all linked appointments, and reading the
cancelled linked-booking bubble from the client conversation timeline.
"""

import re
from datetime import datetime, timedelta

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from tests.tempo.scheduling.appointments.appointment_helpers import UI_TIMEOUT, open_calendar_page

SCHEDULE_BTN = 'button[data-qa="multi-booking-modal-Schedule appointment"]'
ADD_SERVICE_BTN = "#add-service-button"


def _app_base(page: Page) -> str:
    return page.url.split("/app/", 1)[0]


def _frames(page: Page):
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator("#vue_iframe_layout")
    return outer, inner


# --------------------------------------------------------------------------- #
# Scheduling
# --------------------------------------------------------------------------- #
def schedule_multi_booking(
    page: Page,
    context: dict,
    service_names: list[str],
    client_name: str,
) -> None:
    """Schedule one linked appointment composed of `service_names` for a client.

    The first service is moved to tomorrow (a guaranteed future slot, matching the
    legacy next_day date); the others inherit that date. The scenario does not
    assert the exact time, so the dialog's default start time is kept.
    """
    open_calendar_page(page)
    outer, inner = _frames(page)

    _open_appointment_dialog(page, outer, inner)
    _select_client(page, outer, inner, client_name)

    _select_service(page, inner, service_names[0])
    _wait_schedule_button(inner)
    _select_tomorrow_date(inner)

    for name in service_names[1:]:
        add_btn = inner.locator(ADD_SERVICE_BTN)
        add_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
        add_btn.click(timeout=UI_TIMEOUT)
        _select_service(page, inner, name)

    schedule_btn = _wait_schedule_button(inner)
    schedule_btn.click(force=True)
    _wait_dialog_closed(inner)


def _wait_dialog_closed(inner) -> None:
    """Wait for the New Appointment dialog to finish submitting and close.

    Submission of the linked appointments is async (the dialog shows a spinner),
    so the schedule button can stay mounted past the 5s UI cap; poll for it to
    detach a few times before giving up.
    """
    schedule_btn = inner.locator(SCHEDULE_BTN)
    for _ in range(4):
        try:
            schedule_btn.wait_for(state="hidden", timeout=UI_TIMEOUT)
            return
        except PlaywrightTimeoutError:
            continue
    raise AssertionError("New Appointment dialog did not close after scheduling")


def _open_appointment_dialog(page: Page, outer, inner) -> None:
    new_btn = inner.get_by_role("button", name="New")
    new_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    new_btn.click(timeout=UI_TIMEOUT)
    appointment_option = inner.get_by_role("menuitem", name="Appointment", exact=True)
    appointment_option.wait_for(state="visible", timeout=UI_TIMEOUT)
    appointment_option.click(timeout=UI_TIMEOUT)
    outer.get_by_role("dialog").wait_for(state="visible", timeout=UI_TIMEOUT)


def _select_client(page: Page, outer, inner, client_name: str) -> None:
    search_field = outer.get_by_role("textbox", name="Search by name, email or tag")
    search_field.click(timeout=UI_TIMEOUT)
    page.wait_for_timeout(100)
    search_field.press_sequentially(client_name, delay=30)
    client_option = outer.get_by_role("button").filter(has_text=client_name)
    client_option.wait_for(state="visible", timeout=UI_TIMEOUT)
    client_option.click(timeout=UI_TIMEOUT)
    service_picker = inner.locator('[data-qa="service-picker-modal"]:visible')
    service_picker.wait_for(state="visible", timeout=UI_TIMEOUT)


def _select_service(page: Page, inner, service_name: str) -> None:
    service_picker = inner.locator('[data-qa="service-picker-modal"]:visible')
    service_picker.wait_for(state="visible", timeout=UI_TIMEOUT)
    search = service_picker.get_by_role("searchbox", name="Search")
    search.click(timeout=UI_TIMEOUT)
    page.wait_for_timeout(100)
    search.press_sequentially(service_name, delay=30)
    service_row = service_picker.locator(".service-item").filter(has_text=service_name).first
    service_row.wait_for(state="visible", timeout=UI_TIMEOUT)
    service_row.locator('[data-qa="service-name"]').click(timeout=UI_TIMEOUT)
    service_picker.wait_for(state="hidden", timeout=UI_TIMEOUT)


def _wait_schedule_button(inner):
    schedule_btn = inner.locator(f"{SCHEDULE_BTN}:not([disabled])").first
    schedule_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    return schedule_btn


def _select_tomorrow_date(inner) -> None:
    tomorrow = datetime.now() + timedelta(days=1)
    date_input = inner.locator("[data-qa='date-picker-text-input']").first
    date_input.wait_for(state="visible", timeout=UI_TIMEOUT)
    date_input.click(timeout=UI_TIMEOUT)

    # If tomorrow rolls into the next month, advance the picker one month.
    if tomorrow.month != datetime.now().month:
        inner.locator(
            ".date-picker-menu-content .v-date-picker-header > button:nth-child(3)"
        ).first.click(timeout=UI_TIMEOUT)

    day_button = inner.locator(
        ".date-picker-menu-content .v-date-picker-table table:not([class]) button"
    ).filter(has_text=re.compile(rf"^{tomorrow.day}$")).last
    day_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    day_button.click(timeout=UI_TIMEOUT)


# --------------------------------------------------------------------------- #
# Back-office appointment page
# --------------------------------------------------------------------------- #
def open_appointment(page: Page, appointment_id: str) -> None:
    page.goto(
        f"{_app_base(page)}/app/appointments/{appointment_id}",
        wait_until="domcontentloaded",
        timeout=UI_TIMEOUT,
    )
    page.wait_for_url("**/app/appointments/**", timeout=UI_TIMEOUT)
    outer, _ = _frames(page)
    outer.get_by_role("heading", name="Appointment").first.wait_for(
        state="visible", timeout=UI_TIMEOUT
    )


def read_appointment_state(page: Page) -> str:
    outer, _ = _frames(page)
    state = outer.locator("[data-qa='appointment-state']")
    state.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return state.first.inner_text(timeout=UI_TIMEOUT).strip()


def appointment_is_free(page: Page) -> bool:
    outer, _ = _frames(page)
    return outer.locator("[data-qa='appointment-free']").count() > 0


def read_linked_booking_description(page: Page) -> str | None:
    """Return the 'Multi-service booking (N)' caption text, or None if unlinked."""
    outer, _ = _frames(page)
    caption = outer.locator("[data-qa='linked-booking-description'] + .caption")
    if caption.count() == 0:
        return None
    return caption.first.inner_text(timeout=UI_TIMEOUT).strip()


def linked_booking_count(description: str) -> str:
    match = re.search(r"\(([^()]*)\)", description or "")
    return match.group(1) if match else ""


def read_linked_booking_services(page: Page) -> list[str]:
    """Open the linked-booking dialog and return the listed service titles."""
    outer, _ = _frames(page)
    dialog_button = outer.locator("[data-qa='linked-booking-dialog-button']")
    dialog_button.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    dialog_button.first.click(timeout=UI_TIMEOUT)
    dialog = outer.locator("[data-qa='linked-booking-dialog']")
    dialog.wait_for(state="visible", timeout=UI_TIMEOUT)
    titles = dialog.locator(".list-item .list-item_title")
    titles.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return [t.strip() for t in titles.all_inner_texts()]


def cancel_appointment_bulk(page: Page, *, cancel_all: bool) -> None:
    """Cancel a linked appointment: single (this one) or all linked appointments."""
    outer, _ = _frames(page)
    cancel_btn = outer.locator("[data-qa='cancel']")
    cancel_btn.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    cancel_btn.first.click(timeout=UI_TIMEOUT)

    wizard = _bulk_cancel_frame(outer)
    confirm = wizard.locator("[data-qa='bulk-action-multi-booking-footer-Confirm']")
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    if not cancel_all:
        single_radio = wizard.locator("[data-qa='radio-single']")
        single_radio.wait_for(state="visible", timeout=UI_TIMEOUT)
        single_radio.click(timeout=UI_TIMEOUT)
    confirm.click(timeout=UI_TIMEOUT)

    cancelled = outer.get_by_text("Cancelled", exact=True)
    cancelled.first.wait_for(state="visible", timeout=UI_TIMEOUT)


def _bulk_cancel_frame(outer):
    """The bulk-cancel dialog renders in a nested Vue iframe on the appointment page.

    Try the wizard iframe first (matches the legacy switchToVueIFrame target on
    this page); fall back to the layout iframe if the confirm button is there.
    """
    for frame_id in ("#vue_wizard_iframe", "#vue_iframe_layout"):
        frame = outer.frame_locator(frame_id)
        try:
            frame.locator("[data-qa='bulk-action-multi-booking-footer-Confirm']").wait_for(
                state="visible", timeout=UI_TIMEOUT
            )
            return frame
        except PlaywrightTimeoutError:
            continue
    raise AssertionError("Bulk-cancel confirm button not found in any Vue iframe")


# --------------------------------------------------------------------------- #
# Client conversation timeline
# --------------------------------------------------------------------------- #
def read_last_linked_booking_bubble(page: Page, client_id: str, *, attempts: int = 12) -> dict:
    """Read the client's last linked-booking conversation bubble.

    Returns {"services": [...], "labels": [...], "text": "..."} for the last
    linked-booking bubble, mirroring the legacy getLastEntityBubbleData. The
    conversation is rendered in a nested Vue iframe whose id can vary, so this
    scans every frame for the bubble and polls because the bubble reaches the
    timeline asynchronously (legacy waited on the same eventual delivery).
    """
    page.goto(
        f"{_app_base(page)}/app/clients/{client_id}",
        wait_until="domcontentloaded",
        timeout=UI_TIMEOUT,
    )
    page.wait_for_url("**/app/clients/**", timeout=UI_TIMEOUT)

    for _ in range(attempts):
        for frame in page.frames:
            try:
                bubbles = frame.query_selector_all("div.linked-booking-bubble")
            except Exception:
                continue
            if not bubbles:
                continue
            bubble = bubbles[-1]
            services = [e.inner_text().strip() for e in bubble.query_selector_all("span.msgbl-title")]
            labels = [e.inner_text().strip() for e in bubble.query_selector_all(".msgbl-text-label")]
            return {"services": services, "labels": labels, "text": bubble.inner_text().strip()}
        page.wait_for_timeout(1000)

    raise AssertionError("Cancelled linked-booking bubble did not appear in the conversation")
