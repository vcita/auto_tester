# Cancel single multi-booking appointment — script

## Entry
`test_cancel_single(page, context)` — uses `mb_service_names`, `mb_client_name`.

## Locators (multi_booking_ui.py)
- Frames: outer `iframe[title="angularjs"]`, inner `#vue_iframe_layout`.
- Schedule dialog: New button (role) → Appointment menuitem → client search
  `textbox[name="Search by name, email or tag"]` → service picker
  `[data-qa="service-picker-modal"]` → service row `.service-item` →
  `[data-qa="service-name"]`.
- Add another service: `#add-service-button`.
- Schedule button: `button[data-qa="multi-booking-modal-Schedule appointment"]:not([disabled])`.
- Appointment page: state `[data-qa='appointment-state']`, free
  `[data-qa='appointment-free']`, linked caption
  `[data-qa='linked-booking-description'] + .caption`, linked dialog
  `[data-qa='linked-booking-dialog-button']` / `[data-qa='linked-booking-dialog']`
  / `.list-item .list-item_title`.
- Cancel: `[data-qa='cancel']` → nested Vue iframe
  (`#vue_wizard_iframe` / `#vue_iframe_layout`) →
  `[data-qa='radio-single']` (single) → `[data-qa='bulk-action-multi-booking-footer-Confirm']`.

## Flow
1. Snapshot appointment ids (API), schedule the 3-service booking via UI.
2. Diff appointment ids → 3 new; map `title`→id (title == service name).
3. Open service1 appointment → cancel single.
4. Re-open service1 → assert state CANCELLED, Free, linked description is None.
5. For service2/service3 → assert SCHEDULED, Free, linked description contains
   "Multi-service booking", count == 2, linked dialog lists both remaining services.

## Scope preservation vs legacy
- Multi-booking scheduling is fully UI-driven (legacy `scheduleMultiBookingAppointment`
  via Quick Actions; here via the equivalent calendar New → Appointment dialog,
  same Vue service-picker + `#add-service-button` + `multi-booking-modal-Schedule appointment`).
- Single cancel uses the same bulk-cancel dialog and `radio-single` + Confirm
  (legacy `cancelMultiBookingAppointment(false)`).
- All legacy `meeting created with details` assertions are preserved: CANCELLED
  state + Free price + `is_linked_booking false` for service1; SCHEDULED + Free +
  `is_linked_booking true` + linked count (2) + linked services list for service2/3.

## Notes / intentional differences
- The appointment is opened by id via `/app/appointments/<id>` (legacy navigates
  the same URL with the id resolved from the appointments list API). The id is
  resolved by diffing the appointments list before/after scheduling, mirroring the
  legacy `addBookingToContext` behavior, instead of keeping a Selenium scenario
  context.
- Date/time on the first service uses tomorrow + 09:00 AM (legacy next_day + 09:00 AM).
