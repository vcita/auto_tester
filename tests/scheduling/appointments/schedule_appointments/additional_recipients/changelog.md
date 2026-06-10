# Changelog — Schedule Appointment With Additional Recipients

## 2026-06-09 — Initial migration (VCITA2-14025)

- Migrated from `automation-js/features/tempo/scheduling-appointments.feature` scenario 2.
- Schedules two appointments adding an additional recipient (typed email, then "from list")
  and verifies `[data-qa='additional-recipients']` on each detail page.
- Added `_add_additional_recipients` to `schedule_appointments_ui.py` and an
  `additional_recipients` assertion to `assert_meeting`.
