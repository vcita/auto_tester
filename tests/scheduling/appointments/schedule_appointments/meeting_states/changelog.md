# Changelog — Schedule Appointments With Different Meeting States

## 2026-06-11 — Stabilize inline new-client email field

- Fixed flaky inline new-client creation (`_fill_dynamic_email` in
  `schedule_appointments_ui.py`). The email field is an AngularJS `md-autocomplete`
  "dynamic field" that perpetually animates, so Playwright `fill`/`type` time out on the
  visibility+stability actionability gate (and char-by-char input is swallowed by the
  autocomplete). Now the value is set directly on the attached node via JS with
  `input`/`change` events to drive `ng-model`, re-asserted until it reads back on two
  consecutive checks (survives a digest before Save) within a documented dynamic-field
  budget. Mirrors legacy `enterTextToDynamicField` (enter + validate + retry). Removes the
  flakiness that previously failed under stress.

## 2026-06-09 — Initial migration (VCITA2-14025)

- Migrated from `automation-js/features/tempo/scheduling-appointments.feature` scenario 1.
- Schedules three appointments exercising INVITED (client confirmation), SCHEDULED
  (future all-day) and COMPLETED (past) states, with inline new-client and inline new-staff
  creation and assigned-staff selection.
- Added `_open_appointment_dialog` (existing/new client), `_create_client_inline`,
  `_select_assigned_staff`, `_create_and_select_staff`, `_toggle_all_day` and the
  `assigned_staff` / `meeting_date` assertions to `schedule_appointments_ui.py`.
