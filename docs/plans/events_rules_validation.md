# Events Category – Rules Validation Report

**Date**: 2026-01-26  
**Scope**: All tests under `tests/scheduling/events/` (_setup, schedule_event, view_event, add_attendee, remove_attendee, edit_event, cancel_event)

## Summary

| Rule Area | Status | Notes |
|-----------|--------|-------|
| Navigation (no reload/goto internal) | ✅ Pass | No `page.reload()`, `page.goto()`, or `page.refresh()` to internal URLs |
| Outcome verification (state-changing) | ✅ Pass | All state-changing tests verify outcome; steps.md updated where needed |
| Text input (press_sequentially) | ✅ Pass | Text fields use press_sequentially; fill() only for number spinbuttons (documented) |
| script.md VERIFIED PLAYWRIGHT CODE | ✅ Pass | Every action step has VERIFIED PLAYWRIGHT CODE blocks |
| steps.md Expected Result | ✅ Pass | Expected Result states what to assert; aligned with implementation |
| UI navigation only | ✅ Pass | Navigation via Calendar/Event List/Calendar View menus and buttons |
| Wait strategy (no arbitrary waits) | ✅ Pass | All long `wait_for_timeout` replaced with event-based waits (see §8) |

---

## 1. Navigation Rules (heal.mdc / phase3)

- **Rule**: No `page.reload()` or `page.goto()` to internal app URLs. Only login URL is allowed for entry.
- **Check**: Grep for `reload|goto(|refresh` in events tests.
- **Result**: ✅ **Pass** – No matches. Comments like “Allow calendar to refresh” refer to waiting, not calling `page.reload()`.

---

## 2. Outcome Verification (phase1_steps.mdc)

- **Rule**: For any state-changing step (create, update, delete, cancel, add, remove), the test must verify the real-world outcome, not only that the UI flow completed.
- **Check**: steps.md and test.py for explicit verification steps and Expected Result wording.

| Test | State change | Verification in test | steps.md alignment |
|------|----------------|----------------------|--------------------|
| _setup | Create service, create client | Service name saved; client created message; navigate to Calendar | ✅ |
| schedule_event | Create event | Event visible in Event List (search + get_by_text) | ✅ Updated: step 7 and Expected Result mention Event List |
| view_event | — | URL + headings visible | ✅ |
| add_attendee | Add attendee | Attendees tab shows (1); client in list | ✅ |
| remove_attendee | Remove attendee | Count 0 + “cancelled by” indicator | ✅ |
| edit_event | Edit event | Max attendance 12 visible | ✅ |
| cancel_event | Cancel event | CANCELLED in Event List row (closest list-item text) | ✅ Updated: step 4 and Expected Result say CANCELLED in Event List |

- **Result**: ✅ **Pass** – All state-changing flows have clear outcome checks; steps.md updated for schedule_event and cancel_event to match implementation.

---

## 3. Text Input (phase2_script.mdc / phase3_code.mdc)

- **Rule**: Use `press_sequentially()` for text input; `fill()` only for documented exceptions (e.g. number spinbuttons).
- **Check**: Grep for `.fill(` in events tests.
- **Result**: ✅ **Pass** – `fill()` appears only for:
  - `_setup`: max_attendees and price (comments: “fill is OK for number spinbutton”).
  - `edit_event`: max_attendance (comment: “fill is OK for number spinbutton”).
  All other text input uses `press_sequentially()`.

---

## 4. script.md Structure (phase2_script.mdc)

- **Rule**: Each action step must include VERIFIED PLAYWRIGHT CODE, How verified, Wait for.
- **Check**: VERIFIED PLAYWRIGHT CODE block count and structure per script.
- **Result**: ✅ **Pass** – All 7 event scripts contain multiple VERIFIED PLAYWRIGHT CODE blocks with step-wise code and verification notes.

---

## 5. steps.md Expected Result (phase1_steps.mdc)

- **Rule**: Expected Result must state what to assert (e.g. “Event is marked as CANCELLED in Event List”), not only “dialog closes” or “navigates to calendar.”
- **Check**: Each test’s steps.md Expected Result and verification steps.
- **Result**: ✅ **Pass** – Every test has Expected Result describing observable outcomes (e.g. “Client appears in the attendees list”, “Attendee no longer appears”, “Event is shown as CANCELLED in Event List”). schedule_event and cancel_event updated to match current implementation.

---

## 6. Context / Prerequisites Consistency

- **Check**: schedule_event docstring and steps.md say it saves only `scheduled_event_time`; `scheduled_event_id` is set by view_event.
- **Result**: ✅ **Pass** – schedule_event steps.md Expected Result updated to list only `scheduled_event_time` and to note that `scheduled_event_id` is set by View Event.

---

## 7. Minor Notes (No Change Required)

- **expect() vs wait_for()**: view_event and edit_event use `expect(...).to_be_visible()` after navigation. Phase3 prefers `locator.wait_for(state='visible')` before or in addition to expect for robustness. Current usage is acceptable and tests pass; consider adding explicit `wait_for(state='visible')` in future if flakiness appears.
- **schedule_event step 7**: Implementation verifies in Event List; steps.md now says “Verify event was created (e.g. appears in Event List)” and Expected Result mentions “Event List (or calendar)”.

---

## 8. Wait Strategy / No Arbitrary Waits (phase3_code.mdc, phase2_script.mdc)

- **Rule**: Do not use arbitrary time waits. Always wait for a concrete event (element state, URL, list loaded, etc.) with a timeout. Never assume "wait X seconds" is enough. Only use `wait_for_timeout()` for small allowed delays (e.g. 100–300ms before typing, 200–500ms settle after an element wait).
- **Check**: Grep for `wait_for_timeout(1000)` and above in `tests/scheduling/events/**/*.py`; classify as allowed (≤500ms with comment) or replace with event-based wait.
- **Result**: ✅ **Pass** – All events tests updated: **cancel_event** (event_list_item, search field, menuitem, dialog hidden); **schedule_event** (dropdown, dialog, combobox, listbox, option, date-picker, event-list search, dialog hidden); **view_event** (event menuitem visible); **edit_event** (registered_text visible); **add_attendee** (client option, Continue visible); **_setup** (dialog hidden); **remove_attendee** (URL/element/dialog/count-based waits). script.md can be aligned when scripts are next regenerated.

---

## Files Updated During Validation

- `tests/scheduling/events/schedule_event/steps.md` – Step 7 and Expected Result aligned with Event List verification; context list corrected (scheduled_event_time only).
- `tests/scheduling/events/cancel_event/steps.md` – Step 4 and Expected Result clarified to “CANCELLED (e.g. in Event List)”.

- For **wait strategy (§8)**: All events `test.py` files were updated to remove arbitrary `wait_for_timeout(1000+)` and use event-based waits; script.md files were not edited (can be aligned when scripts are next regenerated).
