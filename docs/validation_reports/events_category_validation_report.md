# Events Category – Rules Validation Report

**Date**: 2026-01-31  
**Scope**: Events category — all tests under `tests/scheduling/events/`

**Resolved test list**:
- `tests/scheduling/events/_setup`
- `tests/scheduling/events/_teardown`
- `tests/scheduling/events/schedule_event`
- `tests/scheduling/events/view_event`
- `tests/scheduling/events/add_attendee`
- `tests/scheduling/events/remove_attendee`
- `tests/scheduling/events/edit_event`
- `tests/scheduling/events/cancel_event`

**Summary**: 12 rule areas; 8 Pass, 4 Fail, 0 N/A.

---

## Summary Table

| Rule Area | Status | Notes |
|-----------|--------|-------|
| 1. Navigation (no reload/goto internal) | ❌ Fail | _teardown/script.md documents page.goto to /app/dashboard in VERIFIED PLAYWRIGHT CODE |
| 2. Outcome verification | ✅ Pass | State-changing tests verify outcome; steps.md Success Criteria align |
| 3. Text input (press_sequentially) | ✅ Pass | .fill() only for number spinbuttons with comments |
| 4. script.md VERIFIED PLAYWRIGHT CODE | ✅ Pass | All scripts have VERIFIED PLAYWRIGHT CODE blocks |
| 5. steps.md Expected Result | ✅ Pass | Expected Result / Success Criteria state observable outcomes |
| 6. Wait strategy (no arbitrary waits) | ✅ Pass | All wait_for_timeout ≤500 ms with allowed/Brief/Polling comments |
| 7. Context / prerequisites consistency | ✅ Pass | Docstrings and steps.md agree on context |
| 8. Matter entity name agnosticism | ✅ Pass | "Register Clients" is event UI; no hardcoded matter-only locators |
| 9. No retries for actions | ❌ Fail | remove_attendee: try click then except force click (retry same action) |
| 10. Test cleanup and teardown | ✅ Pass | _teardown deletes client then service; context cleared |
| 11. No fallbacks for detection | ❌ Fail | remove_attendee, add_attendee, cancel_event, _teardown/script.md |
| 12. Timeout means failure | ❌ Fail | remove_attendee, add_attendee: catch and try alternative instead of failing |

---

## 1. Navigation (no reload/goto internal)

- **Rule**: No `page.reload()`, `page.goto()`, or `page.refresh()` to internal app URLs. Only login or public entry points allowed.
- **Source**: `.cursor/rules/heal.mdc`, `.cursor/rules/phase3_code.mdc`
- **Check**: Grep for `reload|goto\(|\.refresh\(` in test.py and script.md under events.
- **Result**: ❌ **Fail**
- **Details**: `tests/scheduling/events/_teardown/script.md` contains **page.goto(.../app/dashboard)** in multiple VERIFIED PLAYWRIGHT CODE blocks (e.g. lines 90, 107, 148, 165, 183), documented as "Fallback: navigate to dashboard via URL (allowed for error recovery)". **test.py** does not use page.goto — it uses UI (Return to homepage, Dashboard link). Script.md is out of sync and documents a forbidden pattern; even if intended as product-bug workaround, it must be explicitly documented as such and preferably removed in favor of UI navigation to match test.py.

---

## 2. Outcome verification (state-changing steps)

- **Rule**: For any state-changing step (create, update, delete, cancel, add, remove), the test must verify the outcome; Expected Result must state what to assert.
- **Source**: `.cursor/rules/phase1_steps.mdc`
- **Check**: steps.md and test.py for state-changing steps and Success Criteria.

| Test | State change | Verification in test | steps.md alignment |
|------|--------------|----------------------|--------------------|
| _setup | Create service, client | Service name in context; service visible on Services page; navigate to Calendar | ✅ |
| schedule_event | Create event | Event in Event List (search + get_by_text) | ✅ |
| view_event | — | URL + headings visible | ✅ |
| add_attendee | Add attendee | Attendees (1); client in list | ✅ |
| remove_attendee | Remove attendee | Count 0 + "Canceled by" indicator | ✅ |
| edit_event | Edit event | Max attendance 12 visible | ✅ |
| cancel_event | Cancel event | CANCELLED in Event List | ✅ |
| _teardown | Delete client, service | Functions perform delete; error-page handling; context cleared | ✅ |

- **Result**: ✅ **Pass**

---

## 3. Text input (press_sequentially)

- **Rule**: Use `press_sequentially()` for text input; `fill()` only for documented exceptions (e.g. number spinbutton).
- **Source**: `.cursor/rules/phase2_script.mdc`, `.cursor/rules/phase3_code.mdc`
- **Check**: Grep for `.fill(` in test.py and script.md.
- **Result**: ✅ **Pass**
- **Details**: `.fill()` only in _setup (max_attendees, price) and edit_event (max_attendance), each with comment "fill is OK for number spinbutton".

---

## 4. script.md structure (VERIFIED PLAYWRIGHT CODE)

- **Rule**: Each action step must include VERIFIED PLAYWRIGHT CODE, How verified, and Wait for.
- **Source**: `.cursor/rules/phase2_script.mdc`
- **Check**: Each script.md for VERIFIED PLAYWRIGHT CODE blocks per action step.
- **Result**: ✅ **Pass**
- **Details**: All 8 scripts (including _setup, _teardown) have VERIFIED PLAYWRIGHT CODE blocks and verification/wait notes.

---

## 5. steps.md Expected Result

- **Rule**: Expected Result / Success Criteria must state what to assert, not only "dialog closes" or "navigates to …".
- **Source**: `.cursor/rules/phase1_steps.mdc`
- **Check**: Each test's steps.md Expected Result / Success Criteria.
- **Result**: ✅ **Pass**
- **Details**: All tests have Expected Result or Success Criteria describing observable outcomes (event in list, status CANCELLED, attendees count, etc.).

---

## 6. Wait strategy (no arbitrary waits)

- **Rule**: No arbitrary long time waits; use event-based waits with long timeout. `wait_for_timeout()` only for small allowed delays (e.g. 100–500 ms) with comment.
- **Source**: `.cursor/rules/phase3_code.mdc`, `.cursor/rules/phase2_script.mdc`
- **Check**: Grep for `wait_for_timeout` in test.py; ensure ≤500 ms with allowed/Brief/Polling comment.
- **Result**: ✅ **Pass**
- **Details**: All occurrences are ≤500 ms with "allowed", "Brief", or "Polling interval" comments. Event-based waits used for readiness.

---

## 7. Context / prerequisites consistency

- **Rule**: Docstrings and steps.md should agree on context saved/consumed and prerequisites.
- **Source**: `.cursor/rules/phase1_steps.mdc`
- **Check**: Context chain across _setup → schedule_event → view_event → add_attendee → remove_attendee → edit_event → cancel_event → _teardown.
- **Result**: ✅ **Pass**
- **Details**: steps.md and docstrings align on event_group_service_name, event_client_*, scheduled_event_*, etc.; _teardown clears same vars.

---

## 8. Matter entity name agnosticism

- **Rule**: Do not hardcode a single matter entity label in locators; use regex/positional/ADD_MATTER_TEXT_REGEX where entity varies by vertical.
- **Source**: `.cursor/rules/project.mdc`
- **Check**: Grep for hardcoded entity-only strings in test.py and script.md.
- **Result**: ✅ **Pass**
- **Details**: "Register Clients" in add_attendee is event-specific UI (button for event registration dialog), not the generic matter list label. No forbidden matter-only locators (e.g. "Properties", "Delete properties?") in events tests.

---

## 9. No retries for actions

- **Rule**: Do not retry user actions; wait for readiness, then act once.
- **Source**: `.cursor/rules/project.mdc`, `.cursor/rules/phase3_code.mdc`
- **Check**: Grep for retry/retries/for attempt in range in test.py and script.md (excluding _runs); identify retry of same user action.
- **Result**: ❌ **Fail**
- **Details**: **remove_attendee/test.py** lines 99–101, 108–110: `try: attendees_btn.first.click(timeout=10000); except Exception: attendees_btn.first.click(force=True, timeout=5000)` (and similar for attendees_tab). This retries the **same** click with `force=True` — a user-action retry. Rule: wait for element to be actionable (e.g. wait for cover to disappear or use a single reliable interaction), then click once. **Violation**: `tests/scheduling/events/remove_attendee/test.py` — retry click with force=True.

---

## 10. Test cleanup and teardown

- **Rule**: _setup-created objects cleaned in _teardown; create-tests have corresponding delete/cancel; context cleared after deletion.
- **Source**: `.cursor/rules/project.mdc`
- **Check**: _setup creates what; _teardown deletes what; test order and context clearing.

| Category | Setup objects | Teardown cleanup | Test sequence cleanup | Context cleared | Status |
|----------|---------------|-------------------|------------------------|-----------------|--------|
| scheduling/events | event_group_service_name, event_client_* | Delete client (fn_delete_client), delete service (fn_delete_service); error-page handling | schedule_event → cancel_event | _teardown pops all event_* and created_* | ✅ Pass |

- **Result**: ✅ **Pass**

---

## 11. No fallbacks for detection

- **Rule**: One detection per step; no fallback locators or try/except for the same ready condition.
- **Source**: `.cursor/rules/project.mdc`, `.cursor/rules/phase3_code.mdc`
- **Check**: Grep for fallback/try/except patterns that try locator A then locator B for same condition.
- **Result**: ❌ **Fail**
- **Details**:
  - **remove_attendee/test.py**: Try `get_by_text('Cancel registration')`, then except try `locator('*').filter(has_text=...)`, then try outer_iframe, then try page — multiple ways to find the same "Cancel registration" menu item (fallback detection). Lines 52–56: "Fallback: look for events showing 1/10 Registered" for same "find event row" condition. **remove_attendee/script.md** line 180: "Try regex first, fallback to filter".
  - **add_attendee/test.py** lines 58–66: Try wait_for client by name; except try client by email — fallback for same "client visible in results" condition.
  - **cancel_event/test.py**: Multiple frames and fallback locators for same "Cancel Event" button / menu item; "Fallback: any button in row" for menu button.
  - **_teardown/script.md**: Step 0 "Fallback: try Settings then Dashboard"; Step 1 "Fallback: navigate to dashboard via URL" — fallback navigation (and page.goto).
- **Violations**: remove_attendee (test.py + script.md), add_attendee (test.py), cancel_event (test.py), _teardown (script.md).

---

## 12. Timeout means failure

- **Rule**: If a wait times out, the test must fail; do not catch timeout and continue to next step or alternative.
- **Source**: `.cursor/rules/project.mdc`, `.cursor/rules/phase3_code.mdc`
- **Check**: try/except around waits that continue or try alternative instead of failing.
- **Result**: ❌ **Fail**
- **Details**:
  - **remove_attendee/test.py**: try submit_btn click / wait_for, except pass; then try other confirm button names (lines 386–418). If the first wait or click times out, the test tries alternatives instead of failing. Lines 254–327: try get_by_text('Cancel registration') with polling, except try filter, try outer_iframe, try page — on timeout/exception, try another way (timeout/exception swallowed for same condition).
  - **add_attendee/test.py** lines 58–66: try `client_locator.first.wait_for(state='visible', timeout=15000)`; except try client by email and wait_for. If "client by name" times out, test tries "client by email" instead of failing.
- **Violations**: remove_attendee/test.py (catch and try next button / next locator); add_attendee/test.py (catch timeout and try email locator).

---

## Files to update (optional)

- **Rule 1 (Navigation)**  
  - `tests/scheduling/events/_teardown/script.md`: Remove or replace `page.goto(.../app/dashboard)` in VERIFIED PLAYWRIGHT CODE with UI navigation (Return to homepage, Dashboard link) to match test.py. If page.goto is kept as product-bug workaround, document explicitly as such in script and changelog.

- **Rule 9 (No retries)**  
  - `tests/scheduling/events/remove_attendee/test.py`: Replace "try click, except force click" with a single strategy: e.g. wait for element to be actionable (e.g. wait for overlay hidden or scroll into view + single click). Do not retry the same click with force=True.

- **Rule 11 (No fallbacks)**  
  - `tests/scheduling/events/remove_attendee/test.py` and `script.md`: One way to find "Cancel registration" (e.g. inner_iframe + one locator); one way to find event row. Remove fallback locators and try/except chains for same condition.  
  - `tests/scheduling/events/add_attendee/test.py`: One way to find client in results (e.g. by name with long timeout); if not found, fail. Remove "try name except try email" fallback.  
  - `tests/scheduling/events/cancel_event/test.py`: Single strategy to find Cancel Event button / menu (document chosen approach); remove fallback frames/locators for same action.  
  - `tests/scheduling/events/_teardown/script.md`: Remove "Fallback: try Settings" and "Fallback: page.goto"; align with test.py (UI-only navigation).

- **Rule 12 (Timeout means failure)**  
  - `tests/scheduling/events/remove_attendee/test.py`: Do not catch timeout/exception and try alternative locators or buttons; on timeout, fail. Use one confirmation button and one way to find "Cancel registration".  
  - `tests/scheduling/events/add_attendee/test.py`: On client-not-found timeout, fail; do not catch and try email.

---

*Validation performed per `.cursor/commands/validate_tests.md` and rule files in `.cursor/rules/`.*
