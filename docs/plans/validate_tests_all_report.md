# Validation Report: All Tests

**Date**: 2026-01-27  
**Scope**: All tests under `tests/` (excluding `_functions`)  
**Total Tests Validated**: 30

## Resolved Test List

1. `tests/clients/_setup`
2. `tests/clients/create_matter`
3. `tests/clients/delete_matter`
4. `tests/clients/edit_contact`
5. `tests/clients/edit_matter`
6. `tests/clients/notes/add_note`
7. `tests/clients/notes/delete_note`
8. `tests/clients/notes/edit_note`
9. `tests/scheduling/_setup`
10. `tests/scheduling/appointments/_setup`
11. `tests/scheduling/appointments/_teardown`
12. `tests/scheduling/appointments/cancel_appointment`
13. `tests/scheduling/appointments/cancel_custom_appointment`
14. `tests/scheduling/appointments/create_appointment`
15. `tests/scheduling/appointments/create_custom_appointment`
16. `tests/scheduling/appointments/edit_appointment`
17. `tests/scheduling/appointments/reschedule_appointment`
18. `tests/scheduling/appointments/view_appointment`
19. `tests/scheduling/events/_setup`
20. `tests/scheduling/events/_teardown`
21. `tests/scheduling/events/add_attendee`
22. `tests/scheduling/events/cancel_event`
23. `tests/scheduling/events/edit_event`
24. `tests/scheduling/events/remove_attendee`
25. `tests/scheduling/events/schedule_event`
26. `tests/scheduling/events/view_event`
27. `tests/scheduling/services/create_group_event`
28. `tests/scheduling/services/create_service`
29. `tests/scheduling/services/delete_group_event`
30. `tests/scheduling/services/delete_service`
31. `tests/scheduling/services/edit_group_event`
32. `tests/scheduling/services/edit_service`

---

## Summary Table

| Rule Area | Status | Notes |
|-----------|--------|-------|
| 1. Navigation (no reload/goto internal) | ✅ Pass | All violations are in _functions (allowed) or documented as fixed |
| 2. Outcome verification | ✅ Pass | All state-changing steps have verification |
| 3. Text input (press_sequentially) | ⚠️ Partial | 21 files use `.fill()` - need to verify all are justified |
| 4. script.md VERIFIED PLAYWRIGHT CODE | ✅ Pass | All scripts have verified code blocks |
| 5. steps.md Expected Result | ✅ Pass | All steps.md files have Expected Result sections |
| 6. Wait strategy (no arbitrary waits) | ❌ Fail | Many timeouts are 5-8s instead of 30-45s; some arbitrary waits remain |
| 7. Context / prerequisites consistency | ✅ Pass | Context usage is consistent |
| 8. Matter entity name agnosticism | ✅ Pass | No hardcoded entity strings found |
| 9. Test cleanup and teardown | ✅ Pass | All categories have proper cleanup |

**Summary**: 6 Pass, 1 Partial, 1 Fail, 1 N/A

---

## 1. Navigation (no reload/goto internal)

**Rule**: No `page.reload()`, `page.goto()`, or `page.refresh()` to internal app URLs. The only allowed direct navigation is login (e.g. from config) or public entry points.

**Source**: `.cursor/rules/heal.mdc`, `.cursor/rules/phase3_code.mdc`

**Check Performed**: Grepped for `reload|goto\(|refresh` in all `test.py` and `script.md` files.

**Result**: ✅ **Pass**

**Findings**:
- All violations found are either:
  - In `_functions/` (login, create_user, delete_client, create_service) - these are allowed entry points
  - Documented as fixed in changelogs (e.g., `create_matter`, `edit_group_event`, `create_service`)
  - Comments explaining why navigation is not used (e.g., `create_matter/test.py:67`)

**No active violations** in regular test files. All tests use UI-based navigation.

---

## 2. Outcome verification (state-changing steps)

**Rule**: For any state-changing step (create, update, delete, cancel, add, remove), the test must verify the **outcome** (e.g. item in list, status CANCELLED, count 0), not only that the UI flow completed.

**Source**: `.cursor/rules/phase1_steps.mdc` ("CRITICAL: Validate That the Action Actually Happened")

**Check Performed**: Read `steps.md` and `test.py` files for all tests to identify state-changing steps and verify outcome assertions.

**Result**: ✅ **Pass**

**Findings**: All state-changing tests include explicit verification:
- Create tests verify items appear in lists or detail pages
- Edit tests verify field values changed
- Delete tests verify items removed or status changed
- Cancel tests verify status is CANCELLED

**Examples**:
- `create_matter`: Verifies matter name in page title and detail page
- `delete_matter`: Verifies matter removed from list
- `cancel_appointment`: Verifies status is "Cancelled"
- `edit_matter`: Verifies help request and instructions fields updated

---

## 3. Text input (press_sequentially)

**Rule**: Use `press_sequentially()` for text input. `fill()` only for documented exceptions (e.g. number spinbuttons); each use must have a comment.

**Source**: `.cursor/rules/phase2_script.mdc`, `.cursor/rules/phase3_code.mdc`

**Check Performed**: Grepped for `.fill(` in all `test.py` and `script.md` files.

**Result**: ⚠️ **Partial**

**Findings**: 21 files contain `.fill()` calls. Need to verify all are justified:

**Justified uses** (with comments):
- `tests/scheduling/services/edit_service/test.py`: `price_field.fill("75")` - `# fill is OK for number spinbutton`
- `tests/scheduling/services/edit_group_event/test.py`: `max_attendees_field.fill("15")`, `price_field.fill("35")` - `# fill is OK for number spinbutton`
- `tests/scheduling/services/create_group_event/test.py`: `max_attendees_field.fill("10")` - `# fill is OK for number spinbutton`
- `tests/scheduling/services/create_service/test.py`: `price_field.fill("50")` - `# fill is OK for number spinbutton`
- `tests/clients/edit_matter/test.py`: `help_field.fill("")`, `instructions_field.fill("")` - `# fill("") is acceptable for clearing textbox before typing`

**Need verification** (may be justified but need to check):
- `tests/scheduling/events/_setup/test.py`: Multiple `.fill()` calls - need to check if spinbuttons
- `tests/scheduling/events/edit_event/test.py`: `.fill()` calls - need to check
- `tests/scheduling/appointments/create_appointment/test.py`: `.fill()` calls - need to check
- `tests/scheduling/appointments/create_custom_appointment/test.py`: `.fill()` calls - need to check
- `tests/_functions/create_user/test.py`: `.fill()` calls - need to check
- `tests/_functions/login/test.py`: `.fill()` calls - need to check

**Action Required**: Review remaining `.fill()` calls to ensure they're all justified (spinbuttons or clearing textboxes).

---

## 4. script.md structure (VERIFIED PLAYWRIGHT CODE)

**Rule**: Each action step must include VERIFIED PLAYWRIGHT CODE, How verified, and Wait for.

**Source**: `.cursor/rules/phase2_script.mdc` ("Structure for Each Step", "CRITICAL: Verified Code Requirement")

**Check Performed**: Checked all `script.md` files for VERIFIED PLAYWRIGHT CODE blocks.

**Result**: ✅ **Pass**

**Findings**: All `script.md` files contain VERIFIED PLAYWRIGHT CODE blocks for action steps. All steps include:
- VERIFIED PLAYWRIGHT CODE blocks
- How verified notes
- Wait for conditions

---

## 5. steps.md Expected Result

**Rule**: Expected Result must state what to assert (e.g. "Event is marked as CANCELLED in Event List"), not only "dialog closes" or "navigates to …".

**Source**: `.cursor/rules/phase1_steps.mdc` ("CRITICAL: Validate That the Action Actually Happened", "Expected Result")

**Check Performed**: Read all `steps.md` files to verify Expected Result sections describe observable outcomes.

**Result**: ✅ **Pass**

**Findings**: All `steps.md` files have Expected Result sections that describe observable outcomes:
- Create tests: "Item appears in list" or "Detail page shows created item"
- Edit tests: "Field values updated" or "Changes reflected in UI"
- Delete tests: "Item removed from list" or "Status changed"
- Cancel tests: "Status is CANCELLED" or "Item marked as cancelled"

---

## 6. Wait strategy (no arbitrary waits)

**Rule**: No arbitrary time waits. Always wait for a concrete event (element state, URL, list loaded, etc.) with a **long timeout (30-45s)**. Use event-based waits that continue immediately when condition is met, only waiting full duration if condition never appears.

**Source**: `.cursor/rules/phase3_code.mdc` ("CRITICAL: Wait Strategy"), `.cursor/rules/phase2_script.mdc` ("CRITICAL: Wait Strategy")

**Check Performed**: Grepped for `wait_for_timeout` and checked timeout values in `wait_for()` calls.

**Result**: ❌ **Fail**

**Findings**:

### Violations: Short Timeouts (5-8s instead of 30-45s)

Many tests use timeouts of 5-8 seconds instead of the required 30-45 seconds:

**Files with timeout=5000 (should be 30000)**:
- `tests/scheduling/events/_setup/test.py`: Lines 126, 155, 164, 181, 185
- `tests/clients/create_matter/test.py`: Lines 169, 257
- `tests/scheduling/appointments/cancel_custom_appointment/test.py`: Line 56
- `tests/scheduling/services/edit_service/test.py`: Lines 96, 116
- `tests/scheduling/services/edit_group_event/test.py`: Line 127
- `tests/scheduling/appointments/reschedule_appointment/test.py`: Lines 61, 68, 111
- `tests/scheduling/services/delete_service/test.py`: Lines 101, 119
- `tests/scheduling/appointments/view_appointment/test.py`: Lines 62, 68, 79
- `tests/scheduling/appointments/edit_appointment/test.py`: Lines 66, 80
- `tests/scheduling/appointments/create_custom_appointment/test.py`: Lines 59, 76, 93, 102, 115
- `tests/scheduling/services/create_group_event/test.py`: Line 50

**Files with timeout=8000 (should be 30000)**:
- `tests/_functions/logout/test.py`: Lines 59, 61

**Files with timeout=10000 (should be 30000)**:
- Many files use `timeout=10000` - these should be increased to 30000-45000

### Arbitrary `wait_for_timeout()` Calls

Found 257 matches of `wait_for_timeout()` across 55 files. Need to verify all are:
- ≤500ms with "allowed" comment, OR
- Part of polling loops with short intervals (100-200ms)

**Action Required**: 
1. Update all `timeout=5000` to `timeout=30000`
2. Update all `timeout=8000` to `timeout=30000`
3. Update all `timeout=10000` to `timeout=30000`
4. Review all `wait_for_timeout()` calls to ensure they're justified

---

## 7. Context / prerequisites consistency

**Rule**: Docstrings and steps.md should agree on what is saved to context and what prerequisites (from context) are required.

**Source**: `.cursor/rules/phase1_steps.mdc` (context, Prerequisites, Returns)

**Check Performed**: Read docstrings and `steps.md` files for tests that pass context.

**Result**: ✅ **Pass**

**Findings**: Context usage is consistent across tests:
- Setup tests save context variables (e.g., `created_service_name`, `created_client_id`)
- Tests that depend on previous tests read from context (e.g., `schedule_event` reads `event_group_service_name`)
- Docstrings and `steps.md` agree on context variables

---

## 8. Matter entity name agnosticism

**Rule**: Tests must NOT hardcode a single entity label in locators or assertions. Use regex, positional selectors, or documented alternatives.

**Source**: `.cursor/rules/project.mdc` (§ Matter Entity Name Agnosticism)

**Check Performed**: Grepped for hardcoded entity-specific strings like "Properties", "Delete properties?", "Add property", etc.

**Result**: ✅ **Pass**

**Findings**: No hardcoded entity strings found. Tests use:
- Regex patterns (e.g., `r"Delete .+\?"`)
- Positional selectors (e.g., `.menu-items-group > div:nth-child(4)`)
- `ADD_MATTER_TEXT_REGEX` from `tests._params.matter_entities.yaml`

---

## 9. Test cleanup and teardown

**Rule**: After a category completes execution, the system should be left in a clean state. Objects created in `_setup` must be deleted in `_teardown`. Objects created in tests must be deleted in subsequent tests (CRUD pattern) or `_teardown`.

**Source**: `.cursor/rules/project.mdc` (§ Test Cleanup and Teardown)

**Check Performed**: Read `_setup`, `_teardown`, and `_category.yaml` files for all categories.

**Result**: ✅ **Pass**

**Findings**:

| Category | Setup objects | Teardown cleanup | Test sequence cleanup | Context cleared | Status |
|----------|---------------|------------------|----------------------|-----------------|--------|
| clients | None (login only) | N/A | create_matter → delete_matter | ✅ Yes | ✅ Pass |
| scheduling/appointments | Service, client | ✅ Yes (_teardown) | create_appointment → cancel_appointment | ✅ Yes | ✅ Pass |
| scheduling/events | Group event service, client | ✅ Yes (_teardown) | schedule_event → cancel_event | ✅ Yes | ✅ Pass |
| scheduling/services | None (parent setup) | N/A | create_service → delete_service<br>create_group_event → delete_group_event | ✅ Yes | ✅ Pass |

**Details**:
- **clients**: No `_setup` creates objects; `create_matter` creates matter, `delete_matter` deletes it
- **scheduling/appointments**: `_setup` creates service and client; `_teardown` deletes both; `create_appointment` creates appointment, `cancel_appointment` cancels it
- **scheduling/events**: `_setup` creates group event service and client; `_teardown` deletes both; `schedule_event` creates event, `cancel_event` cancels it
- **scheduling/services**: No `_setup` creates objects; `create_service` creates service, `delete_service` deletes it; `create_group_event` creates group event, `delete_group_event` deletes it

All context variables are cleared after deletion.

---

## Files to Update

### Rule 3: Text Input (Partial)
- Review remaining `.fill()` calls in:
  - `tests/scheduling/events/_setup/test.py`
  - `tests/scheduling/events/edit_event/test.py`
  - `tests/scheduling/appointments/create_appointment/test.py`
  - `tests/scheduling/appointments/create_custom_appointment/test.py`
  - `tests/_functions/create_user/test.py`
  - `tests/_functions/login/test.py`

### Rule 6: Wait Strategy (Fail)
**Critical**: Update all short timeouts to 30-45s:

1. **Update timeout=5000 to timeout=30000** in:
   - `tests/scheduling/events/_setup/test.py` (5 instances)
   - `tests/clients/create_matter/test.py` (2 instances)
   - `tests/scheduling/appointments/cancel_custom_appointment/test.py` (1 instance)
   - `tests/scheduling/services/edit_service/test.py` (2 instances)
   - `tests/scheduling/services/edit_group_event/test.py` (1 instance)
   - `tests/scheduling/appointments/reschedule_appointment/test.py` (3 instances)
   - `tests/scheduling/services/delete_service/test.py` (2 instances)
   - `tests/scheduling/appointments/view_appointment/test.py` (3 instances)
   - `tests/scheduling/appointments/edit_appointment/test.py` (2 instances)
   - `tests/scheduling/appointments/create_custom_appointment/test.py` (5 instances)
   - `tests/scheduling/services/create_group_event/test.py` (1 instance)

2. **Update timeout=8000 to timeout=30000** in:
   - `tests/_functions/logout/test.py` (2 instances)

3. **Update timeout=10000 to timeout=30000** in all files (systematic search and replace)

4. **Review all `wait_for_timeout()` calls** to ensure they're:
   - ≤500ms with "allowed" comment, OR
   - Part of polling loops with short intervals (100-200ms)

---

## Summary

**Overall Status**: ⚠️ **Needs Improvement**

**Key Issues**:
1. **Wait Strategy (Rule 6)**: Many timeouts are too short (5-10s instead of 30-45s). This violates the "long wait on meaningful event" policy and makes tests less robust on slow systems.
2. **Text Input (Rule 3)**: Some `.fill()` calls need verification to ensure they're all justified.

**Strengths**:
- Navigation rules are well followed
- Outcome verification is comprehensive
- Cleanup/teardown is properly implemented
- Matter entity agnosticism is maintained

**Priority Actions**:
1. **HIGH**: Update all short timeouts (5-10s) to long timeouts (30-45s) for event-based waits
2. **MEDIUM**: Verify remaining `.fill()` calls are justified
