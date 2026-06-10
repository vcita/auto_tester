# Changelog — Schedule Appointments With Different Meeting States

## 2026-06-09 — Initial migration (VCITA2-14025)

- Migrated from `automation-js/features/tempo/scheduling-appointments.feature` scenario 1.
- Schedules three appointments exercising INVITED (client confirmation), SCHEDULED
  (future all-day) and COMPLETED (past) states, with inline new-client and inline new-staff
  creation and assigned-staff selection.
- Added `_open_appointment_dialog` (existing/new client), `_create_client_inline`,
  `_select_assigned_staff`, `_create_and_select_staff`, `_toggle_all_day` and the
  `assigned_staff` / `meeting_date` assertions to `schedule_appointments_ui.py`.
