# Changelog: business_settings

## 2026-06-04 — Initial migration (VCITA2-13796)

- Migrated from `automation-js/features/tempo/calendar-settings.feature` scenario
  "Calendar business settings".
- UI ownership preserved: business settings set through the calendar settings side pane
  (Start-week = Tuesday, time format = 24 hours), weekends hidden via the view menu.
- Assertion preserved exactly: Week header `{Tue, 00:00, 5}`.
- Reused `open_calendar_page` and the calendar frame/side-pane helpers; new actions live
  in `calendar_settings_helpers.py`.
- Replaced the legacy fixed sleep in `getCalendarWeekDisplay` with a bounded poll on the
  rendered header values.
