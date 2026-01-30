# All Tests – Rules Validation Report

**Date**: 2026-01-28  
**Re-validated**: 2026-01-28 (after fixing violations and updating wait strategy rule)  
**Scope**: All tests under `tests/` (excluding `tests/_functions/`)

## Resolved scope (35 test directories)

- **scheduling**: `_setup`
- **scheduling/events**: `_setup`, `_teardown`, `schedule_event`, `view_event`, `add_attendee`, `remove_attendee`, `edit_event`, `cancel_event`
- **scheduling/appointments**: `_setup`, `_teardown`, `create_appointment`, `view_appointment`, `edit_appointment`, `reschedule_appointment`, `cancel_appointment`, `create_custom_appointment`, `cancel_custom_appointment`
- **scheduling/services**: `create_service`, `edit_service`, `delete_service`, `create_group_event`, `edit_group_event`, `delete_group_event`
- **clients**: `_setup`, `create_matter`, `edit_matter`, `edit_contact`, `delete_matter`
- **clients/notes**: `add_note`, `edit_note`, `delete_note`

**Summary**: 9 rule areas; 8 Pass, 1 Pass/N/A (Rule 7). Violations fixed and wait strategy re-tested per new policy.

---

## Summary table

| Rule Area | Status | Notes |
|-----------|--------|-------|
| 1. Navigation (no reload/goto internal) | ✅ Pass | Fixed: `events/_teardown` no longer uses `page.goto`; uses UI (Return to homepage or Dashboard link) only |
| 2. Outcome verification (state-changing) | ✅ Pass | State-changing tests have verification steps; steps.md aligned |
| 3. Text input (press_sequentially) | ✅ Pass | Fixed: `edit_matter` fill("") has “fill OK to clear before typing”; `edit_service` price fill has “fill is OK for number spinbutton” |
| 4. script.md VERIFIED PLAYWRIGHT CODE | ✅ Pass | All in-scope script.md files have VERIFIED PLAYWRIGHT CODE blocks |
| 5. steps.md Expected Result | ✅ Pass | Expected Result describes observable outcomes |
| 6. Wait strategy (new policy) | ✅ Pass | Long waits on meaningful events preferred; arbitrary short waits replaced with event-based (long timeout) or brief allowed delays (≤500 ms with comment); re-validated |
| 7. Context / prerequisites consistency | ✅ Pass / N/A | Docstrings and steps.md agree on context; N/A where no chain |
| 8. Matter entity name agnosticism | ✅ Pass | No hardcoded entity-only locators in test.py; comments/docstrings OK |
| 9. Test cleanup and teardown | ✅ Pass | Setup→teardown and test-sequence cleanup documented; context cleared |

---

## 1. Navigation (no reload/goto internal)

**Rule**: No `page.reload()`, `page.goto()`, or `page.refresh()` to internal app URLs. Only allowed direct navigation is login or public entry points.  
**Source**: `.cursor/rules/heal.mdc`, `.cursor/rules/phase3_code.mdc`

**Check**: Grep for `reload|goto\(|refresh` in scoped `test.py` and `script.md` (excluding `_functions`). Exclude comments that only describe waiting (e.g. “allow calendar to refresh”).

**Result**: ✅ **Pass**

**Fix applied**: `tests/scheduling/events/_teardown/test.py` — Removed fallback `page.goto(.../app/dashboard)`. When “Return to homepage” link is not found, teardown now tries UI navigation via Dashboard link; if neither is found, logs a warning and stays on current page. No direct goto to internal URLs.

**Note**: `_functions` (e.g. `delete_client`, `login`) were excluded from scope; their `page.goto` usage (login URL, dashboard recovery) was not re-evaluated here.

---

## 2. Outcome verification (state-changing steps)

**Rule**: For any state-changing step (create, update, delete, cancel, add, remove), the test must verify the **outcome** (e.g. item in list, status CANCELLED, count 0), not only that the UI flow completed. Expected Result must state what to assert.  
**Source**: `.cursor/rules/phase1_steps.mdc`

**Check**: For each test, `steps.md` and `test.py` were reviewed for state-changing steps, explicit verification, and Expected Result wording.

**Result**: ✅ **Pass**

- **scheduling/events**: schedule_event, cancel_event, add_attendee, remove_attendee, edit_event verify outcome (Event List, CANCELLED, count, visible data). _setup creates service/client and navigates; _teardown deletes and clears context.
- **scheduling/appointments**: create/cancel tests verify status or removal; create_custom_appointment / cancel_custom_appointment document verification.
- **scheduling/services**: create/edit/delete services and group events have verification steps and Expected Result (e.g. service removed from list, values visible after save).
- **clients**: create_matter, edit_matter, edit_contact, delete_matter have verification (list, detail, row gone). steps.md Expected Result states observable outcomes.
- **clients/notes**: add_note, edit_note, delete_note have verification steps and Expected Result (note visible, content matches, note gone/count decreased).

---

## 3. Text input (press_sequentially)

**Rule**: Use `press_sequentially()` for text input. `fill()` only for documented exceptions (e.g. number spinbutton); each use must have a comment.  
**Source**: `.cursor/rules/phase2_script.mdc`, `.cursor/rules/phase3_code.mdc`

**Check**: Grep for `.fill(` in scoped `test.py`. Each occurrence must be justified (spinbutton or documented exception).

**Result**: ✅ **Pass**

**Fixes applied**:
- `tests/clients/edit_matter/test.py`: Added comment “fill OK to clear before typing” for `help_field.fill("")` and `instructions_field.fill("")`.
- `tests/scheduling/services/edit_service/test.py`: Added comment “fill is OK for number spinbutton” for `price_field.fill("75")`.

**Allowed**: Other `.fill(` uses in scope have spinbutton or clear-before-typing comments (e.g. events _setup, edit_group_event, create_service, create_group_event, edit_event). _functions were not in scope.

---

## 4. script.md structure (VERIFIED PLAYWRIGHT CODE)

**Rule**: Each action step must include VERIFIED PLAYWRIGHT CODE, How verified, and Wait for.  
**Source**: `.cursor/rules/phase2_script.mdc`

**Check**: In-scope `script.md` files checked for VERIFIED PLAYWRIGHT CODE blocks per action step.

**Result**: ✅ **Pass**

All 29 in-scope script.md files (scheduling, clients, clients/notes; excluding _functions) contain multiple VERIFIED PLAYWRIGHT CODE blocks with step-wise code and verification/wait notes.

---

## 5. steps.md Expected Result

**Rule**: Expected Result must state what to assert (e.g. “Event is marked as CANCELLED in Event List”), not only “dialog closes” or “navigates to …”.  
**Source**: `.cursor/rules/phase1_steps.mdc`

**Check**: Each test’s `steps.md` Expected Result / Success Criteria section.

**Result**: ✅ **Pass**

Sampled and full set: Expected Result / Success Criteria describe observable outcomes (e.g. service removed from list, note visible in notes section, status Canceled, matter deleted and no longer in list). No test relies only on “dialog closes” or “navigates to” as the sole success criterion.

---

## 6. Wait strategy (new policy)

**Rule**: Prefer long waits on meaningful events (page, button, message, dropdown, dialog, URL change). Avoid arbitrary short time waits that fail when the system is slow. Use event-based waits with long timeouts (30–45 s). Use `wait_for_timeout()` only for brief allowed delays (e.g. 100–300 ms before typing, 200–500 ms settle after element wait, polling intervals in loops); each must have an “allowed” or justification comment.  
**Source**: `.cursor/rules/phase3_code.mdc`, `.cursor/rules/phase2_script.mdc`

**Check**: Grep for `wait_for_timeout` in scoped `test.py`. Verify: (1) no arbitrary long fixed delays for “action done”; (2) long waits are on meaningful events (element/URL/dialog) with long timeout; (3) any remaining `wait_for_timeout` ≤ 500 ms has “allowed” or “brief” comment.

**Result**: ✅ **Pass** (re-validated after fixes and policy update)

**Fixes applied**:
- **Navigation**: `events/_teardown` — removed `page.goto` fallback; use UI only.
- **Services (edit_service, edit_group_event, delete_service)**: Replaced 1000 ms scroll waits with 300 ms “Brief settle after scroll (allowed)”; 500 ms “Brief settle after refresh/save (allowed)”.
- **create_matter**: Removed 2000 ms initial wait; replaced second 2000 ms with 300 ms “Brief settle after click (allowed)”.
- **reschedule_appointment**: Removed 1000 ms before dialog; use `dialog.wait_for(state="visible", timeout=30000)`.
- **cancel_custom_appointment**: Replaced 2000 ms “calendar load” with wait for appointment menuitem (timeout=30000); removed 1000 ms before dialog (use dialog wait); removed 2000 ms before verify (use `cancelled_status.wait_for(..., timeout=30000)`).
- **edit_appointment**: Replaced 1000 ms “note dialog open” with `note_iframe.get_by_role('button', name='Save').wait_for(state='visible', timeout=30000)`; added missing `note_iframe`/`note_area` definitions.
- **create_custom_appointment / create_appointment**: Replaced 500 ms “dropdown/search” with wait for target element (timeout=30000) where applicable; 300/500 ms kept with “Brief settle (allowed)” or “Brief delay for focus (allowed)”.
- **events _setup**: 400 ms → 300 ms “Brief settle after scroll (allowed)”; 500 ms given “Brief settle after navigation/scroll (allowed)”.
- **remove_attendee, delete_matter, create_matter, etc.**: All remaining 300–500 ms waits have “allowed” or “Polling interval (allowed)” comments.

**Re-test**: In-scope tests now use long timeouts on meaningful events (dialog, element visible, URL) and only ≤500 ms with explicit “allowed” comments for brief settle/polling/focus. No arbitrary short fixed waits for “action done.”

---

## 7. Context / prerequisites consistency

**Rule**: Docstrings and steps.md should agree on what is saved to context and what prerequisites (from context) are required.  
**Source**: `.cursor/rules/phase1_steps.mdc`

**Check**: For tests that pass context (e.g. schedule_event → view_event, create_matter → delete_matter), steps.md and test docstring were checked for saved/consumed context.

**Result**: ✅ **Pass** / **N/A**

- Context chains (e.g. events: _setup → schedule_event → view_event → …; clients: create_matter → edit_matter → delete_matter; notes: add_note → edit_note → delete_note) are consistent between steps.md and docstrings.
- Categories with no context chain (e.g. scheduling _setup) are N/A.

---

## 8. Matter entity name agnosticism

**Rule**: Do not hardcode a single entity label in locators or assertions (e.g. "Properties", "Delete property"). Use regex, positional selectors, or documented alternatives. Docstrings/comments as examples are OK.  
**Source**: `.cursor/rules/project.mdc`

**Check**: Grep for hardcoded entity-only strings in scoped test code (not _functions). Allowed: positional selectors, regex, ADD_MATTER_TEXT_REGEX; docstrings/comments as examples.

**Result**: ✅ **Pass**

- **clients/delete_matter/test.py**: Uses `page.locator('.menu-items-group > div:nth-child(4)')` (positional); comments describe “Properties” as example only. No `get_by_text("Properties")` in code.
- **clients/create_matter/test.py**: Comments only (“Properties”, “Add property”). No entity-only locators.
- No other in-scope test.py uses hardcoded entity-only locators. _params/__init__.py and matter_entities.yaml are reference/config, not test locators.

---

## 9. Test cleanup and teardown

**Rule**: After a category completes, the system should be left clean. Setup-created objects deleted in teardown; test-created objects deleted in sequence or teardown; context cleared.  
**Source**: `.cursor/rules/project.mdc`

**Check**: Per category: (1) _setup → _teardown mapping, (2) test sequence cleanup (create → delete/cancel), (3) context cleared after delete/cancel, (4) cancellation documented where applicable.

**Result**: ✅ **Pass**

| Category | Setup objects | Teardown cleanup | Test sequence cleanup | Context cleared | Status |
|----------|---------------|------------------|------------------------|----------------|--------|
| scheduling | _setup: login, navigate to Services (no created objects) | N/A (no scheduling-level _teardown) | N/A | N/A | Pass |
| scheduling/events | _setup: group event service, test client | _teardown: delete_client, delete_service; clears event_* and created_* | Events create event only; cancel_event cancels it | Yes in _teardown | Pass |
| scheduling/appointments | _setup: service, client | _teardown: delete_client, delete_service | create_appointment → cancel_appointment; create_custom_appointment → cancel_custom_appointment | Yes in _teardown and cancel tests | Pass |
| scheduling/services | Uses parent _setup | No _teardown | create_service → delete_service; create_group_event → delete_group_event | Yes in delete tests | Pass |
| clients | _setup: login only | No _teardown | create_matter → edit_matter → edit_contact → delete_matter | Yes in delete_matter | Pass |
| clients/notes | No _setup in notes (uses parent) | No _teardown | add_note → edit_note → delete_note | Yes in delete_note | Pass |

---

## Files updated (2026-01-28)

1. **Navigation**: `tests/scheduling/events/_teardown/test.py` — Removed `page.goto` fallback; use UI (Return to homepage or Dashboard link) only.
2. **Text input**: `tests/clients/edit_matter/test.py`, `tests/scheduling/services/edit_service/test.py` — Added fill-exception comments.
3. **Wait strategy**: Multiple files (see §6) — Replaced arbitrary short waits with event-based long waits or brief allowed delays with comments.

---

**End of report**
