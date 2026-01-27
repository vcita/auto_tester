# Validate Tests

Validate a list of tests and/or categories against all project rules defined in `.cursor/rules/`. Produces a structured report (summary table + per-rule sections with Pass/Fail and notes).

**Usage**: `/validate_tests` [categories and/or test names]

Examples:
- `/validate_tests scheduling/events` — validate all tests in that category
- `/validate_tests Schedule Event Cancel Event` — validate those tests only
- `/validate_tests scheduling/events clients` — validate both categories
- `/validate_tests` — validate all tests under `tests/` (no functions unless you add `_functions`)

**Reference report**: `docs/plans/events_rules_validation.md` shows the expected format and level of detail.

---

## 1. Resolve scope

**Input** (from user):

- **Categories**: Paths like `scheduling/events`, `scheduling/services`, `clients`, `clients/notes`. Validate all tests (and `_setup` / `_teardown` where present) under that category.
- **Tests**: Names or IDs like `Schedule Event`, `schedule_event`, `Cancel Event`. Match by test folder name (`schedule_event`) or by test name in `_category.yaml` / UI; include that test’s folder only.
- **Mix**: User may pass both categories and individual tests.
- **No input**: If nothing is specified, validate **all** tests under `tests/` (excluding `tests/_functions/` unless the user includes functions).

**How to resolve:**

- Base path: `tests/` (workspace root relative).
- Category path: `tests/{category_path}/` (e.g. `tests/scheduling/events/`). Every folder under it that contains `steps.md` (and optionally `script.md`, `test.py`) is a test; also include `_setup` and `_teardown` folders.
- Test name/ID: Scan `tests/` for folders whose name matches the ID (e.g. `schedule_event`) or whose `_category.yaml` / parent category lists a matching name; use that folder as one test.
- Functions: Only if user asked for `_functions` or “functions”, include `tests/_functions/*` (each function folder = one test).

**Output**: A concrete list of test directories (e.g. `tests/scheduling/events/schedule_event`, `tests/scheduling/events/_setup`, …). Confirm the resolved list at the start of the report.

---

## 2. Rule definitions (sources)

Use these rule files as the **definition of what to validate**. Perform each check and note Pass/Fail and any violations.

### 2.1 Navigation (no reload/goto internal)

**Sources**: `.cursor/rules/heal.mdc`, `.cursor/rules/phase3_code.mdc`

- **Rule**: No `page.reload()`, `page.goto()`, or `page.refresh()` to internal app URLs. The only allowed direct navigation is login (e.g. from config) or public entry points.
- **Check**: In each resolved test, grep for `reload|goto\(|refresh` in `test.py` and `script.md`. Exclude comments that only describe waiting (e.g. “allow calendar to refresh”).
- **Report**: Pass if no forbidden calls in scoped files; Fail with file:line/violation list otherwise.

### 2.2 Outcome verification (state-changing steps)

**Source**: `.cursor/rules/phase1_steps.mdc` (“CRITICAL: Validate That the Action Actually Happened”)

- **Rule**: For any state-changing step (create, update, delete, cancel, add, remove), the test must verify the **outcome** (e.g. item in list, status CANCELLED, count 0), not only that the UI flow completed. Expected Result must state what to assert, not only “dialog closes” or “navigates to …”.
- **Check**: For each test, read `steps.md` and `test.py`. Identify state-changing steps and ensure there is an explicit verification step or assertion and that Expected Result describes observable outcomes.
- **Report**: Per-test table: Test | State change | Verification in test | steps.md alignment (Pass/Fail + short note).

### 2.3 Text input (press_sequentially)

**Sources**: `.cursor/rules/phase2_script.mdc` (“CRITICAL: Text Input Method”), `.cursor/rules/phase3_code.mdc` (“Text Input Pattern”)

- **Rule**: Use `press_sequentially()` for text input. `fill()` only for documented exceptions (e.g. number spinbuttons); each use must have a comment (e.g. “fill is OK for number spinbutton”).
- **Check**: Grep for `.fill(` in scoped `test.py` and `script.md`. Each occurrence must be justified (spinbutton or documented exception).
- **Report**: Pass if no unjustified `fill()`; Fail with file:line and list allowed exceptions.

### 2.4 script.md structure (VERIFIED PLAYWRIGHT CODE)

**Source**: `.cursor/rules/phase2_script.mdc` (“Structure for Each Step”, “CRITICAL: Verified Code Requirement”)

- **Rule**: Each action step must include VERIFIED PLAYWRIGHT CODE, How verified, and Wait for.
- **Check**: In each `script.md`, ensure every action step has a VERIFIED PLAYWRIGHT CODE block and verification/wait notes.
- **Report**: Pass if all scripts meet this; Fail with list of scripts/steps missing verified code.

### 2.5 steps.md Expected Result

**Source**: `.cursor/rules/phase1_steps.mdc` (“CRITICAL: Validate That the Action Actually Happened”, “Expected Result”)

- **Rule**: Expected Result must state what to assert (e.g. “Event is marked as CANCELLED in Event List”), not only “dialog closes” or “navigates to …”.
- **Check**: Each test’s `steps.md` must have an Expected Result section that describes observable outcomes.
- **Report**: Pass/Fail per test with short note.

### 2.6 Wait strategy (no arbitrary waits)

**Sources**: `.cursor/rules/phase3_code.mdc` (“CRITICAL: Wait Strategy”), `.cursor/rules/phase2_script.mdc` (“CRITICAL: Wait Strategy”)

- **Rule**: No arbitrary time waits. Always wait for a concrete event (element state, URL, list loaded, etc.) with a **long timeout (30-45s)**. Use event-based waits (`wait_for()`, `wait_for_url()`, etc.) that continue immediately when the condition is met, only waiting the full duration if the condition never appears. Only use `wait_for_timeout()` for small allowed delays (e.g. 100–300 ms before typing, 200–500 ms settle after element wait, or polling intervals in loops); never use it alone for action completion.
- **Check**: In scoped `test.py` (and `script.md` if desired), grep for `wait_for_timeout`. Any call > 500 ms (or without a preceding event-based wait) is a violation unless justified. Allow only ≤500 ms with an “allowed” / “brief” comment.
- **Report**: Pass if no forbidden long waits and event-based waits use long timeouts (30-45s); Fail with file:line and suggested replacement (event-based wait with long timeout) where possible.

### 2.7 Context / prerequisites consistency (optional)

**Source**: `.cursor/rules/phase1_steps.mdc` (context, Prerequisites, Returns)

- **Rule**: Docstrings and steps.md should agree on what is saved to context and what prerequisites (from context) are required.
- **Check**: For tests that pass context (e.g. schedule_event → view_event), ensure steps.md and test docstring match saved/consumed context.
- **Report**: Pass/Fail with short note; can be “N/A” for tests with no context chain.

### 2.8 Matter entity name agnosticism

**Source**: `.cursor/rules/project.mdc` (§ Matter Entity Name Agnosticism)

- **Rule**: The matter entity name varies by vertical (clients, properties, patients, students, pets, etc.). Tests must NOT hardcode a single entity label in locators or assertions. Use regex, positional selectors, or documented alternatives so tests work across verticals.
- **Check**: In each resolved test (and related _functions), grep for hardcoded entity-specific strings: literals like "Properties", "Delete properties?", "Properties deleted", "Add property", "Delete property" (menuitem), or the pattern "1 SELECTED OF \d+ PROPERTIES" as the only match. **Allowed**: positional selectors; regex that accept multiple labels (e.g. `r"1 SELECTED OF \d+"`, `r"Delete .+\?"`); for "Add &lt;entity&gt;" use **`tests._params.ADD_MATTER_TEXT_REGEX`** (entity list in `tests/_params/matter_entities.yaml`) — prefer this over inlining the entity list. Docstrings that mention "Properties"/"Clients" as examples are OK; the check targets locators and assertions.
- **Report**: Pass if no forbidden hardcoded entity-only locators; Fail with file:line and offending string.

### 2.9 Test cleanup and teardown

**Source**: `.cursor/rules/project.mdc` (§ Test Cleanup and Teardown)

- **Rule**: After a category completes execution, the system should be left in a clean state. Objects created in `_setup` must be deleted in `_teardown`. Objects created in tests must be deleted in subsequent tests (CRUD pattern) or `_teardown`. Objects that cannot be deleted should be cancelled/marked as inactive (documented). Context variables must be cleared after deletion.
- **Check**: For each category (or resolved test scope):
  1. **Setup → Teardown mapping**: If `_setup` exists, check if `_teardown` exists and deletes objects created in setup. Read `_setup/test.py` and `_setup/steps.md` to identify created objects (context variables like `created_service_id`, `created_client_id`, etc.). Then check `_teardown/test.py` and `_teardown/steps.md` to verify cleanup.
  2. **Test sequence cleanup**: For tests that create objects (e.g., `create_matter`, `create_service`, `create_appointment`), check if there's a corresponding delete/cancel test later in the sequence (e.g., `delete_matter`, `delete_service`, `cancel_appointment`). Read `_category.yaml` to understand test order.
  3. **Context variable clearing**: Check that delete/cancel tests clear context variables (e.g., `del context["created_matter_id"]` or `context["created_matter_id"] = None`).
  4. **Cancellation documentation**: If objects are cancelled instead of deleted (e.g., appointments), verify this is documented in the cancel test or teardown.
- **Report**: Per-category table: Category | Setup objects | Teardown cleanup | Test sequence cleanup | Context cleared | Status (Pass/Fail/N/A + notes). **Pass** if: (1) no `_setup` OR `_setup` objects are cleaned in `_teardown`, (2) all create tests have corresponding delete/cancel tests OR objects are cleaned in `_teardown`, (3) context variables are cleared after deletion. **Fail** if objects are created but never cleaned up. **N/A** if category has no object creation.

---

## 3. Report format

Produce a single validation report.

1. **Header**
   - Date and scope (list of resolved test paths or category paths).
   - Optional: one-line summary (e.g. “8 rule areas, X Pass, Y Fail”).

2. **Summary table**

   | Rule Area | Status | Notes |
   |-----------|--------|-------|
   | 1. Navigation (no reload/goto internal) | ✅ Pass / ❌ Fail | … |
   | 2. Outcome verification | ✅ Pass / ❌ Fail | … |
   | 3. Text input (press_sequentially) | ✅ Pass / ❌ Fail | … |
   | 4. script.md VERIFIED PLAYWRIGHT CODE | ✅ Pass / ❌ Fail | … |
   | 5. steps.md Expected Result | ✅ Pass / ❌ Fail | … |
   | 6. Wait strategy (no arbitrary waits) | ✅ Pass / ❌ Fail | … |
   | 7. Context / prerequisites consistency | ✅ Pass / ❌ Fail / N/A | … |
   | 8. Matter entity name agnosticism | ✅ Pass / ❌ Fail | … |
   | 9. Test cleanup and teardown | ✅ Pass / ❌ Fail / N/A | … |

3. **Per-rule sections**  
   For each rule (1–9), add a section with:
   - Rule (one sentence) and source (rule file).
   - Check performed (what you grepped/read).
   - Result: Pass or Fail (or N/A where applicable).
   - If Fail: file paths, line numbers or step names, and concrete violations (and, for wait strategy, suggested event-based fixes where useful).
   - For rule 2.9 (cleanup): Include per-category table showing setup objects, teardown cleanup, test sequence cleanup, and context clearing status.

4. **Files to update (optional)**  
   If any Fail: list files that should be updated (e.g. `tests/…/steps.md`, `tests/…/test.py`, `tests/…/script.md`) and what to change briefly.

---

## 4. Execution steps

1. **Resolve scope** from user input (categories and/or test names); list all test directories.
2. **Read rule definitions** from `.cursor/rules/` as needed (phase1_steps.mdc, phase2_script.mdc, phase3_code.mdc, heal.mdc) to apply the checks exactly.
3. **Run each check** (grep, file reads) over the resolved test list.
4. **Fill the summary table** and write each numbered rule section with Pass/Fail and details.
5. **Do not modify** test or script files unless the user explicitly asks to fix violations; this command is **validation and reporting only**.

---

## 5. Example invocations

- **Validate one category**: “Validate scheduling/events” → resolve all tests under `tests/scheduling/events/` (including `_setup`), run all rules, output report.
- **Validate specific tests**: “Validate Schedule Event and Cancel Event” → resolve to those test folders (e.g. under `scheduling/events`), run all rules, output report.
- **Validate multiple categories**: “Validate scheduling/events and clients” → resolve all tests under both category paths, run all rules, output report.
- **Validate everything**: “Validate all tests” or “Validate” with no target → resolve all tests under `tests/` (excluding `_functions` unless requested), run all rules, output report.
