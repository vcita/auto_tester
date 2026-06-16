# Changelog — Appointment With Arrival Window

## 2026-06-10 — Initial build (VCITA2-14025)

- Migrated `scheduling-appointments.feature` scenario 4 ("appointment with arrival window").
- Phases touched: steps.md, script.md, test.py.
- Scope: account-default vs service-override arrival windows, in-dialog preset (`2 hours`) and
  custom (`Custom 75`) overrides, and a reschedule-only arrival-window change (`30 minutes`).
  Each is verified on the appointment detail page (`.arrival-window-time`) and in the client
  notification email (automation message-content API, `Estimated arrival time:` + window).
- Added API helpers `set_account_arrival_window` (account default 45m, set in `_setup`) and
  `set_service_arrival_window` (service2 = 15m). `service2` is created via API in-test.
- Added UI helpers `_add_arrival_window` (dialog `.arrival-window-dropdown` + custom sub-selects)
  and reschedule support for `arrival_window` (`.arrival-window-select`); `assert_meeting` now
  checks the detail-page arrival window.
