# Changelog — Reschedule And Cancel Appointment

## 2026-06-09 — Initial migration (VCITA2-14025)

- Migrated from `automation-js/features/tempo/scheduling-appointments.feature` scenario 3
  ("reschedule and cancel appointment").
- Schedules a past appointment (COMPLETED), reschedules to next week (SCHEDULED) via the
  detail-page Kendo datetime dialog, then cancels (CANCELLED), verifying state + start/end
  times at each step.
- UI primitives added to `schedule_appointments_ui.py` (date navigation past/future, start/end
  time pickers, reschedule Kendo typing, cancel, detail verification); API setup in
  `schedule_appointments_api.py`.
