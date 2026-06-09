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
    price_override: dict | None = None,
) -> str:
    """Schedule an appointment via the BO calendar dialog and return the new appointment id.

    The id is resolved by snapshotting the business appointments before/after (legacy
    addBookingToContext picked the booking not yet seen). ``additional_staff`` (display
    names) are selected through the additional-staff picker before submitting.
    ``price_override`` (``{"fee_type": "No Fee"|"Custom price"|"Fixed price",
    "amount": str|None}``) overrides the service price in the dialog's price panel,
    mirroring the legacy ``setMeetingPrice``/``selectAppointmentPriceType``.
    """
    before_ids = list_appointment_ids(context)
    open_calendar_page(page)
    outer, inner = _frames(page)

    _open_new_appointment(page, outer, inner, client_name)
    _pick_service(page, inner, service_name)

    _schedule_button(inner).wait_for(state="visible", timeout=UI_TIMEOUT)
    _set_future_date(page, inner)
    _set_start_time(inner, "10:00 AM")
    _fill_address_if_present(page, inner)
    if additional_staff:
        _select_additional_staff(page, inner, additional_staff)
    if price_override:
        _apply_price_override(page, inner, price_override)

    submit = _schedule_button(inner)
    submit.wait_for(state="visible", timeout=UI_TIMEOUT)
    submit.click(force=True)
    return _wait_for_new_appointment(page, context, before_ids)


def _open_new_appointment(page: Page, outer, inner, client_name: str) -> None:
    """Open the New Appointment dialog and select the client.

    The client (created via API in _setup) occasionally has not surfaced in the dialog's
    client search within one timeout (CRM indexing lag -> "ALL CLIENTS" empty). Re-opening
    the dialog re-issues the search, so retry the whole open+search (1 + 2) rather than
    failing on a transient empty result.
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
            search = outer.get_by_role("textbox", name="Search by name, email or tag")
            search.click(timeout=UI_TIMEOUT)
            page.wait_for_timeout(100)
            search.press_sequentially(client_name, delay=30)
            client_option = outer.get_by_role("button").filter(has_text=client_name)
            client_option.wait_for(state="visible", timeout=UI_TIMEOUT)
            client_option.click(timeout=UI_TIMEOUT)

            service_picker = inner.locator('[data-qa="service-picker-modal"]:visible')
            service_picker.wait_for(state="visible", timeout=UI_TIMEOUT)
            return
        except PlaywrightTimeoutError as exc:
            last_error = exc
    raise last_error or AssertionError("Service picker did not open after client selection")


def _dismiss_open_dialog(page: Page, outer) -> None:
    """Best-effort close of an appointment dialog left open by a failed attempt."""
    if outer.get_by_role("dialog").count() == 0:
        return
    cancel = outer.get_by_role("button", name=re.compile(r"^Cancel$", re.I)).first
    for closer in (
        lambda: cancel.click(timeout=2_000),
        lambda: page.keyboard.press("Escape"),
    ):
        try:
            closer()
        except Exception:  # noqa: BLE001 - try the next closer
            continue
        page.wait_for_timeout(_SETTLE_MS)
        if outer.get_by_role("dialog").count() == 0:
            return


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


def _set_future_date(page: Page, inner, days_ahead: int = 3) -> None:
    """Move the appointment to a date `days_ahead` in the future and verify it landed.

    This is REQUIRED, not best-effort: the dialog defaults to today, and once the
    appointment start time is in the past the meeting becomes COMPLETED and its
    additional-staff edit link is no longer rendered. `multi_staff_meeting` then can
    never remove a staff. The legacy default-date behaviour only "passed" when the
    suite ran early enough in the account's timezone that today's slot was still
    upcoming; this makes the future date deterministic regardless of run time.
    """
    target = datetime.now() + timedelta(days=days_ahead)

    # The appointment dialog's start-date field. `[data-qa="date-picker-text-input"]` is the
    # readonly <input> itself, so its value is read via input_value (not inner_text).
    date_input = (
        inner.locator('[data-qa="service-date-input"]').first
        .locator('[data-qa="date-picker-text-input"]').first
    )
    before = (date_input.input_value(timeout=UI_TIMEOUT) or "").strip()
    date_input.click(timeout=UI_TIMEOUT)

    # IMPORTANT: scope to the dialog's date-picker popup. The calendar page also has an
    # always-visible mini-calendar (another v-date-picker), so an unscoped `.first` would
    # drive the sidebar instead of the appointment date field.
    menu = inner.locator(".date-picker-menu-content")
    header = menu.locator(".v-date-picker-header__value").first
    table = menu.locator(".v-date-picker-table--date").first
    table.wait_for(state="visible", timeout=UI_TIMEOUT)

    target_label = target.strftime("%B %Y").lower()
    for _ in range(13):  # bounded month navigation (>=1 year of headroom)
        if target_label in (header.inner_text(timeout=UI_TIMEOUT) or "").lower():
            break
        menu.locator(".v-date-picker-header button").last.click(timeout=UI_TIMEOUT)
        page.wait_for_timeout(_SETTLE_MS)

    # Adjacent-month cells share the same table: leading cells are the previous
    # month's high days, trailing cells the next month's low days. So a low target
    # day is the first match and a high target day is the last in-month match.
    day_cells = table.locator("button.v-btn").filter(
        has_text=re.compile(rf"^\s*{target.day}\s*$")
    )
    cell = day_cells.first if target.day <= 14 else day_cells.last
    cell.wait_for(state="visible", timeout=UI_TIMEOUT)
    # Vuetify v-btn day cells ignore a plain Playwright click (ripple overlay swallows it),
    # so dispatch the click event directly to fire Vue's @input handler.
    cell.dispatch_event("click")

    # The date field is the source of truth; it must change away from today's default.
    # A no-op (the original silent bug) leaves a today/past appointment that is COMPLETED
    # and therefore has no additional-staff edit link for the removal step.
    for _ in range(int(UI_TIMEOUT / _SETTLE_MS)):
        after = (date_input.input_value() or "").strip()
        if after and after != before:
            return
        page.wait_for_timeout(_SETTLE_MS)
    raise AssertionError(
        f"Appointment date did not advance to {target:%Y-%m-%d} (date field still {before!r}); "
        "a non-future appointment would be COMPLETED and not editable."
    )


def _set_start_time(inner, time_text: str) -> None:
    try:
        start = inner.locator('[data-qa="service-start-time-input"] input').first
        start.click(timeout=UI_TIMEOUT)
        inner.locator(f'[data-qa="item-{time_text}"]').first.click(timeout=UI_TIMEOUT)
    except Exception:  # noqa: BLE001 - a future date already guarantees an editable (SCHEDULED) meeting
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


_NEW_APPOINTMENT_BUDGET_MS = 12_000  # bounded poll; the legacy flow waited up to 15s for
# the created booking to surface (UI create + API propagation), so a 12s read-back poll is
# justified and still tighter than legacy.
_READBACK_POLL_MS = 1_500  # Poll the appointments-list endpoint gently: a tight 250ms loop
# across several bookings hammers the per-business APPOINTMENTS quota (429
# APPOINTMENTS_LIMIT_EXCEEDED). A 1.5s interval still resolves the new id (it surfaces in
# 1-2s) with ~6x fewer calls.


def _wait_for_new_appointment(page: Page, context: dict, before_ids: set[str]) -> str:
    for _ in range(int(_NEW_APPOINTMENT_BUDGET_MS / _READBACK_POLL_MS)):
        new_ids = list_appointment_ids(context) - before_ids
        if new_ids:
            return next(iter(new_ids))
        page.wait_for_timeout(_READBACK_POLL_MS)
    raise AssertionError("New appointment was not created (no new id appeared in the bookings read-back)")


PRICE_PANEL_HEADER = ".dialog-expansion-panel__price .v-expansion-panel-header"
PRICE_PANEL = ".dialog-expansion-panel__price .v-expansion-panel"
FEE_TYPE_SELECT = ".fee-type-method-selector"
PRICE_INPUT = "[data-qa='price-input'] input"
# FeeTypeGenerator.vue: the "Edit" tax link only renders while chargeTypeIndex===2 and the
# picker is not yet revealed (shouldShowTaxFlow). Once clicked (enableTaxFlow) the TaxPicker
# field (tax-picker-button) is shown; for a service whose picker is already revealed the link
# is absent and the picker shows directly.
EDIT_TAX_LINK = "[data-qa='edit-tax-link']"
TAX_PICKER = "[data-qa='tax-picker-button']"


def _open_price_panel(page: Page, inner) -> None:
    """Expand the appointment dialog's price panel if it is collapsed.

    Idempotent: the fee-type selector is the real "panel open" signal, so only click the
    header when it is not already visible (clicking an already-open header collapses it).
    """
    panel = inner.locator(PRICE_PANEL).first
    panel.wait_for(state="visible", timeout=UI_TIMEOUT)
    fee_select = inner.locator(FEE_TYPE_SELECT).first
    if fee_select.is_visible():
        return
    inner.locator(PRICE_PANEL_HEADER).first.click()
    fee_select.wait_for(state="visible", timeout=UI_TIMEOUT)


def _select_fee_type(page: Page, inner, fee_type: str) -> None:
    """Pick a fee type (No Fee / Custom price / Fixed price) in the price panel.

    Each menu item is a Vuetify list item whose accessible name also includes the
    description line, so match the item's title text rather than the full option name.
    """
    select = inner.locator(FEE_TYPE_SELECT).first
    select.wait_for(state="visible", timeout=UI_TIMEOUT)
    select.click()
    title = inner.locator(".v-list-item__title", has_text=fee_type).first
    title.wait_for(state="visible", timeout=UI_TIMEOUT)
    title.click()


def _select_taxes(page: Page, inner, taxes: list) -> None:
    """Add tax(es) in the appointment price panel (legacy selectTaxes).

    ``taxes`` is ``[(tax_name, rate), ...]``. The TaxPicker (FeeTypeGenerator.vue) shows an
    "Edit" link only when the summary/edit view is active; reveal the picker first when that
    link is present, then open the picker popover and toggle each ``tax-{name}-{rate}``
    VcCheckbox. The checkbox swallows Playwright's synthetic click (Vue overlay), so it is
    toggled via its own DOM ``click`` handler. The popover is closed by clicking the picker
    field again - Escape would close the whole appointment dialog (mirrors the proven
    product_payments tax-picker flow).
    """
    edit_link = inner.locator(EDIT_TAX_LINK).first
    if edit_link.is_visible():
        edit_link.click()
    picker = inner.locator(TAX_PICKER).first
    picker.wait_for(state="visible", timeout=UI_TIMEOUT)
    picker.click()
    for tax_name, rate in taxes:
        option = inner.locator(f'[data-qa="tax-{tax_name}-{rate}"]').first
        option.wait_for(state="visible", timeout=UI_TIMEOUT)
        if not option.is_checked():
            option.evaluate("el => el.click()")
    picker.click()
    page.wait_for_timeout(300)


def _apply_price_override(page: Page, inner, override: dict) -> None:
    """Override the appointment price (fee type / amount / taxes) in the price panel.

    Mirrors the legacy createMeetingDialog.setMeetingPrice / selectAppointmentPriceType /
    selectTaxes. ``fee_type`` and ``amount`` are optional (a tax-only override leaves the
    service's default fee type in place).
    """
    _open_price_panel(page, inner)
    if override.get("fee_type"):
        _select_fee_type(page, inner, override["fee_type"])
    amount = override.get("amount")
    if amount is not None:
        price_input = inner.locator(PRICE_INPUT).first
        price_input.wait_for(state="visible", timeout=UI_TIMEOUT)
        price_input.fill(str(amount))
    if override.get("taxes"):
        _select_taxes(page, inner, override["taxes"])


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
