# Reschedule Appointment Test - Changelog

## 2026-05-27 - Use Visible Unique Time Option

**Phase**: test.py, script.md
**Author**: Cursor AI (stabilization)
**Reason**: Full `scheduling` stress found duplicate hidden Kendo options for `11:00am`, causing strict mode violations.

**Root Cause**: `get_by_text("11:00am", exact=True)` matched more than one rendered option node in the time picker.

**Fix Applied**:
1. Changed the reschedule target to visible `9:30am`, which is different from the create flow's `10:00am`.
2. Scoped selection to visible `li.k-item` dropdown options.
3. Kept all waits capped at 5000ms.

**Scope / Quality**: The test still verifies a real persisted time change and the "Rescheduled from" section; no assertions were removed.

---

## 2026-05-27 - Stabilized Reschedule Time Change

**Phase**: test.py, script.md
**Author**: Cursor AI (stabilization)
**Reason**: `scheduling/appointments` stress failed because reschedule selected `10:00am`, which matched the appointment time created by the stabilized create flow.

**Root Cause**: The test still asserted that the time changed, but the selected reschedule option was no longer different from the initial appointment time.

**Fix Applied**:
1. Changed the reschedule target to `11:00am` so the final time-changed assertion remains meaningful.
2. Reused `open_calendar_page` for calendar navigation.
3. Capped touched waits and navigation waits at 5000ms through `UI_TIMEOUT`.

**Scope / Quality**: The reschedule flow still verifies actual persisted time change and the "Rescheduled from" section; no assertions were removed.

---

## 2026-01-23 - Initial Build

**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration with Playwright MCP.

**Changes**:
- Created steps.md defining appointment reschedule flow.
- Generated script.md from MCP exploration with verified locators.
- Generated test.py from script.md.
