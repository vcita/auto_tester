# Changelog

- Migrated legacy `Calendar - block time`.
- Preserved `@unstable` scope, create, drag, filter, edit, and time assertions.

## 2026-06-10 - Confirm drag landed before reload (shared helper)

**Phase**: Shared helper (`tests/scheduling/calendar/calendar_helpers.py`)
**Author**: Cursor AI
**Reason**: A diagnostic run hit `AssertionError: Calendar items did not match` after dragging a blocked time — `drag_calendar_item` posted the reschedule message and reloaded immediately, racing the scheduler's in-memory `dataSource` update so the reload occasionally showed the item at its old slot.

**Changes**:

- Added `_reschedule_and_confirm`, which posts the reschedule then waits (via the previously dead `_wait_for_scheduler_item_start`) for the moved start to appear in the scheduler `dataSource` before reloading, re-posting once if the first message was dropped. The action targets an absolute slot, so the re-post is idempotent (bounded to 2 attempts).

**Test run**: `scheduling/calendar` headless stress, 10 iterations — **10/10 passed (100%, STABLE)**; Block Time passed every iteration.
