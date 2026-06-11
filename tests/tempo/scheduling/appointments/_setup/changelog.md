# Appointments Setup Changelog

## 2026-05-27 - Stabilized Calendar Loading

**Phase**: appointment_helpers.py, script.md
**Author**: Cursor AI (stabilization)
**Reason**: A 10-iteration stress run failed once in setup with Calendar View stuck on the loading spinner.

**Root Cause**: Sidebar-driven Calendar navigation can reach `/app/calendar` while the inner Calendar app is still loading, and a single 5000ms New-button wait can catch a transient loader.

**Fix Applied**:
1. Changed `open_calendar_page` to prefer direct `/app/calendar` navigation.
2. Added one reload fallback when the Calendar shell is reached but the New button is not visible within the 5000ms window.
3. Kept the Calendar View submenu fallback for route states where direct navigation cannot complete.

**Scope / Quality**: Setup still validates the Calendar New button before tests start; no appointment assertions or test coverage were removed.
