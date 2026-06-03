# Changelog — cancel_single

## Initial migration (VCITA2-13793)
- Migrated from automation-js `features/tempo/multi-booking-appointments.feature`
  scenario "Cancel single multi-booking appointment".
- New isolated subcategory `tests/scheduling/multi_booking`.
- Helpers:
  - `multi_booking_ui.py`: schedule a linked appointment via the calendar New
    dialog (service picker + `#add-service-button` + `multi-booking-modal-Schedule
    appointment`), open a BO appointment by id, read state/free/linked
    description+count, read linked-booking dialog services, cancel single via the
    bulk-cancel dialog.
  - `multi_booking_api.py`: list appointments and diff ids before/after to resolve
    the new appointment ids (mirrors legacy `addBookingToContext`).
- Reused: `fn_login`, `account_api.create_service_via_api` / `create_client`,
  `appointment_helpers.open_calendar_page` / `UI_TIMEOUT`.
- Preconditions (3 services + client) created via API in `_setup`; the staff from
  the legacy Background is omitted (unused by either scenario).
