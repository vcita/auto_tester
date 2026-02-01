# Services Subcategory – Rules Validation Report

**Date**: 2026-01-30  
**Scope**: All tests under `tests/scheduling/services/` (no _setup/_teardown in this subcategory)

**Resolved test list**:
- `tests/scheduling/services/create_group_event`
- `tests/scheduling/services/create_service`
- `tests/scheduling/services/delete_group_event`
- `tests/scheduling/services/delete_service`
- `tests/scheduling/services/edit_group_event`
- `tests/scheduling/services/edit_service`

**Summary**: 10 rule areas; 8 Pass, 0 Fail, 2 N/A. *(All violations fixed 2026-01-30.)*

---

## Summary Table

| Rule Area | Status | Notes |
|-----------|--------|-------|
| 1. Navigation (no reload/goto internal) | ✅ Pass | No `page.reload()`, `page.goto()`, or `page.refresh()` in current code; only comments reference past healing |
| 2. Outcome verification | ✅ Pass | State-changing steps have verification steps and Expected Result describes observable outcomes |
| 3. Text input (press_sequentially) | ✅ Pass | All `.fill()` in script.md documented (number spinbutton / clear); fixed 2026-01-30 |
| 4. script.md VERIFIED PLAYWRIGHT CODE | ✅ Pass | Every action step has VERIFIED PLAYWRIGHT CODE, How verified, Wait for |
| 5. steps.md Expected Result | ✅ Pass | Expected Result states what to assert (list visibility, values, removal) |
| 6. Wait strategy (no arbitrary waits) | ✅ Pass | script.md: 3000ms removed (event-based); 1000ms→300ms in scroll loops; fixed 2026-01-30 |
| 7. Context / prerequisites consistency | N/A | Context chain (create→edit→delete) is documented; no cross-category chain in scope |
| 8. Matter entity name agnosticism | ✅ Pass | No hardcoded Properties/Clients/entity-only locators in services tests |
| 9. No retries for actions | ✅ Pass | `for … in range` is scroll-to-find (list loading), not retry of user actions |
| 10. Test cleanup and teardown | ✅ Pass | No _setup/_teardown; create→delete pairs and context cleared in delete tests |

---

## 1. Navigation (no reload/goto internal)

- **Rule**: No `page.reload()`, `page.goto()`, or `page.refresh()` to internal app URLs. Only login or public entry points allowed.  
- **Source**: `.cursor/rules/heal.mdc`, `.cursor/rules/phase3_code.mdc`
- **Check**: Grep for `reload|goto\(|refresh` in `test.py` and `script.md` under services.
- **Result**: ✅ **Pass**  
- **Details**: Matches are only in comments (e.g. “HEALED 2026-01-27: Replaced page.reload() with UI navigation”) and changelog. No active `page.reload()`, `page.goto()`, or `page.refresh()` in services test code.

---

## 2. Outcome verification (state-changing steps)

- **Rule**: For any state-changing step (create, update, delete, etc.), the test must verify the outcome (e.g. item in list, status, count). Expected Result must state what to assert.  
- **Source**: `.cursor/rules/phase1_steps.mdc`
- **Check**: steps.md and test.py for state-changing steps, verification steps, and Expected Result wording.

| Test | State change | Verification in test | steps.md alignment |
|------|--------------|----------------------|--------------------|
| create_service | Create service | Service in list, open advanced edit, ID from URL | ✅ Expected Result: “New service is created and visible in services list” |
| edit_service | Edit duration/price | Re-open service; duration 45, price 75 | ✅ Expected Result: “Service duration/price updated… Changes persist” |
| delete_service | Delete service | Service no longer in list | ✅ Expected Result: “Service is removed… cannot be found after deletion” |
| create_group_event | Create group event | Group event in list, “10 attendees”, ID from URL | ✅ Expected Result: “Group event appears… showing 10 attendees” |
| edit_group_event | Edit duration/price/max | Values on edit page and in list | ✅ Expected Result: “duration… price… max attendees updated… persist” |
| delete_group_event | Delete group event | Redirect to list; group event not in list | ✅ Expected Result: “removed… cannot be found… returns to services list” |

- **Result**: ✅ **Pass**

---

## 3. Text input (press_sequentially)

- **Rule**: Use `press_sequentially()` for text input. `fill()` only for documented exceptions (e.g. number spinbutton); each use must have a comment.  
- **Source**: `.cursor/rules/phase2_script.mdc`, `.cursor/rules/phase3_code.mdc`
- **Check**: Grep for `.fill(` in scoped `test.py` and `script.md`; each occurrence must be justified.
- **Result**: ✅ **Pass** *(fixed 2026-01-30)*
- **Details**:
  - **test.py**: All `.fill()` uses have comments (“fill is OK for number spinbutton” or “Clear existing value”). ✅
  - **script.md**: All `.fill()` uses now have documented exceptions:
    - `create_service/script.md`: `price_field.fill("50")  # fill is OK for number spinbutton`
    - `edit_service/script.md`: `price_field.fill("")  # Clear existing value`, `price_field.fill("75")  # fill is OK for number spinbutton`
    - `edit_group_event/script.md`: `max_attendees_field.fill("15")`, `price_field.fill("35")` — both with `# fill is OK for number spinbutton`
    - `create_group_event/script.md`: `max_attendees_field.fill("10")`, `price_field.fill("25")` — both with `# fill is OK for number spinbutton`

---

## 4. script.md structure (VERIFIED PLAYWRIGHT CODE)

- **Rule**: Each action step must include VERIFIED PLAYWRIGHT CODE, How verified, and Wait for.  
- **Source**: `.cursor/rules/phase2_script.mdc`
- **Check**: Each `script.md` under services for VERIFIED PLAYWRIGHT CODE blocks and verification/wait notes.
- **Result**: ✅ **Pass**  
- **Details**: All six scripts (create_service, edit_service, delete_service, create_group_event, edit_group_event, delete_group_event) have multiple VERIFIED PLAYWRIGHT CODE blocks with “How verified” and “Wait for” per step.

---

## 5. steps.md Expected Result

- **Rule**: Expected Result must state what to assert (e.g. item in list, values, status), not only “dialog closes” or “navigates to…”.  
- **Source**: `.cursor/rules/phase1_steps.mdc`
- **Check**: Each test’s `steps.md` Expected Result section.
- **Result**: ✅ **Pass**  
- **Details**: All six tests have Expected Result describing observable outcomes (e.g. “New service is created and visible in services list”, “Service is removed from the services list”, “Group event is removed… cannot be found”).

---

## 6. Wait strategy (no arbitrary waits)

- **Rule**: No arbitrary time waits. Use event-based waits with long timeout (30–45s). `wait_for_timeout()` only for small allowed delays (e.g. 100–300 ms before typing, 200–500 ms settle); never alone for action completion.  
- **Source**: `.cursor/rules/phase3_code.mdc`, `.cursor/rules/phase2_script.mdc`
- **Check**: Grep for `wait_for_timeout` in services `test.py` and `script.md`; flag calls >500 ms or without event-based wait.
- **Result**: ✅ **Pass** *(fixed 2026-01-30)*
- **Details**:
  - **test.py**: All `wait_for_timeout` uses are ≤500 ms with “allowed”/“brief” comments. ✅
  - **script.md**: All violations fixed:
    - **create_service/script.md**: Removed `page.wait_for_timeout(3000)`; Step 9 now relies on event-based flow (dialog close, then Step 10 navigation refreshes list). Scroll loop: 1000 ms → 300 ms with “Brief settle (allowed)”.
    - **edit_service/script.md**: Scroll loop 1000 ms → 300 ms with “Brief settle (allowed)”.
    - **edit_group_event/script.md**: Both scroll loops 1000 ms → 300 ms with “Brief settle (allowed)”.
    - **create_group_event/script.md**: Scroll loop 1000 ms → 300 ms with “Brief settle (allowed)”.
    - **delete_service/script.md**: Scroll loop 1000 ms → 300 ms with “Brief settle (allowed)”.

---

## 7. Context / prerequisites consistency

- **Rule**: Docstrings and steps.md should agree on what is saved to context and what prerequisites are required.  
- **Source**: `.cursor/rules/phase1_steps.mdc`
- **Check**: For tests that pass context (create_service → edit_service → delete_service; create_group_event → edit_group_event → delete_group_event), steps.md and test docstrings match.
- **Result**: **N/A** (treated as Pass for reporting)  
- **Details**: Context chain is documented (created_service_name, created_group_event_name, etc.). No cross-category context in scope. Docstrings and steps.md are aligned on context updates and prerequisites.

---

## 8. Matter entity name agnosticism

- **Rule**: Do not hardcode a single matter-entity label (e.g. “Properties”, “Clients”) in locators or assertions; use regex, positional selectors, or `tests._params.ADD_MATTER_TEXT_REGEX` where appropriate.  
- **Source**: `.cursor/rules/project.mdc`
- **Check**: Grep for hardcoded entity-only strings in services tests.
- **Result**: ✅ **Pass**  
- **Details**: No matches for “Properties”, “Delete properties?”, “Add property”, “1 SELECTED OF … PROPERTIES”, or similar entity-only literals in services. Services tests use “Services”, “My Services”, “New service”, etc., which are not matter-entity labels under this rule.

---

## 9. No retries for actions

- **Rule**: Do not retry user actions. Wait for readiness, then perform each action once. No retry loops for clicks, fills, or navigation.  
- **Source**: `.cursor/rules/project.mdc`, `.cursor/rules/phase3_code.mdc`
- **Check**: Grep for `retry|retries|for attempt in range|Retrying:` in test.py and script.md; exclude infrastructure (e.g. scroll-to-find).
- **Result**: ✅ **Pass**  
- **Details**: The only `for … in range(max_scrolls)` loops are scroll-to-find (load more list items until service/group event is visible or end of list). They are not “retry click” or “retry fill”. create_service/changelog and script.md mention past “retry logic”; current test.py does not implement user-action retries.

---

## 10. Test cleanup and teardown

- **Rule**: After category execution, system should be clean. Objects created in setup must be deleted in teardown; objects created in tests deleted in later tests or teardown. Context variables cleared after deletion.  
- **Source**: `.cursor/rules/project.mdc`
- **Check**: _setup/_teardown mapping; test sequence cleanup; context clearing in delete tests.
- **Result**: ✅ **Pass**

| Category | Setup objects | Teardown cleanup | Test sequence cleanup | Context cleared | Status |
|----------|---------------|------------------|------------------------|-----------------|--------|
| scheduling/services | None (no _setup) | N/A | create_service → edit_service → delete_service; create_group_event → edit_group_event → delete_group_event | delete_service: `context.pop` for created_service_* and edited_*; delete_group_event: `context.pop` for created_group_event_* and edited_* | ✅ Pass |

---

## Files updated (2026-01-30)

- **Rule 3 (Text input)** – Added “fill is OK for number spinbutton” (or “Clear existing value”) comments in:
  - `tests/scheduling/services/create_service/script.md`
  - `tests/scheduling/services/edit_service/script.md`
  - `tests/scheduling/services/edit_group_event/script.md`
  - `tests/scheduling/services/create_group_event/script.md`

- **Rule 6 (Wait strategy)** – In script.md only:
  - `create_service`: Removed 3000 ms wait; Step 9 is event-based (dialog close, then Step 10 navigation). Scroll loop: 1000 ms → 300 ms.
  - `edit_service`, `delete_service`, `edit_group_event` (both loops), `create_group_event`: Scroll-loop 1000 ms → 300 ms with “Brief settle (allowed)”.

No test.py changes were required; test code was already compliant.
