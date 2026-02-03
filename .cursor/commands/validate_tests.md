# Validate Tests

Validate a list of tests and/or categories against all project rules defined in `.cursor/rules/`. Produces a structured report (summary table + per-rule sections with Pass/Fail and notes).

**This command defines the validation protocol** (scope resolution, which rules to check, how to run checks, report format). The **authoritative** rule content lives in project.mdc and the phase/build/heal rules; this command **references** those files and defines how to **check** compliance (grep, file reads, Pass/Fail criteria).

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

- **Categories**: Paths like `scheduling/events`, `clients`. Validate all tests (and `_setup` / `_teardown` where present) under that category.
- **Tests**: Names or IDs like `Schedule Event`, `schedule_event`. Match by test folder name or by name in `_category.yaml`; include that test's folder only.
- **Mix**: User may pass both categories and individual tests.
- **No input**: If nothing is specified, validate **all** tests under `tests/` (excluding `tests/_functions/` unless the user includes functions).

**How to resolve:**

- Base path: `tests/`.
- Category path: `tests/{category_path}/`. Every folder under it that contains `steps.md` (and optionally `script.md`, `test.py`) is a test; include `_setup` and `_teardown` folders.
- Test name/ID: Scan `tests/` for folders whose name matches the ID or whose `_category.yaml` / parent category lists a matching name; use that folder as one test.
- Functions: Only if user asked for `_functions` or "functions", include `tests/_functions/*` (each function folder = one test).

**Output**: A concrete list of test directories. Confirm the resolved list at the start of the report.

---

## 2. Rule definitions (sources and checks)

Use the rule files as the **definition of what to validate**. For each rule, the **source** is the authoritative rule; the **check** and **report** below define how to validate and what to output. See the source for full rule text.

### 2.1 Navigation (no reload/goto internal)

**Source**: `.cursor/rules/project.mdc` § Real User Actions Rule; `.cursor/rules/phase3_code.mdc`

- **Rule**: No `page.reload()`, `page.goto()`, or `page.refresh()` to internal app URLs. Only login or public entry points allowed. See project.mdc § Real User Actions Rule for full rule.
- **Check**: In each resolved test, grep for `reload|goto\(|refresh` in `test.py` and `script.md`. Exclude comments that only describe waiting (e.g. "allow calendar to refresh").
- **Report**: Pass if no forbidden calls in scoped files; Fail with file:line/violation list otherwise.

### 2.2 Outcome verification (state-changing steps)

**Source**: `.cursor/rules/phase1_steps.mdc` § CRITICAL: Validate That the Action Actually Happened; `.cursor/rules/phase3_code.mdc` § Assertions and Success Verification

- **Rule**: For state-changing steps (create, update, delete, cancel, add, remove), the test must verify the **outcome** (e.g. item in list, status CANCELLED), not only that the UI flow completed. See phase1_steps.mdc and phase3_code.mdc for full rule.
- **Check**: For each test, read `steps.md` and `test.py`. Identify state-changing steps and ensure there is an explicit verification step or assertion and that Expected Result describes observable outcomes.
- **Report**: Per-test table: Test | State change | Verification in test | steps.md alignment (Pass/Fail + short note).

### 2.3 Text input (press_sequentially)

**Source**: `.cursor/rules/phase2_script.mdc` § CRITICAL: Text Input Method; `.cursor/rules/phase3_code.mdc` § Text Input Pattern

- **Rule**: Use `press_sequentially()` for text input. `fill()` only for documented exceptions (e.g. number spinbutton, clearing field). See phase2_script.mdc and phase3_code.mdc for full rule.
- **Check**: Grep for `.fill(` in scoped `test.py` and `script.md`. Each occurrence must be justified (spinbutton, clear, or documented exception).
- **Report**: Pass if no unjustified `fill()`; Fail with file:line and list allowed exceptions.

### 2.4 script.md structure (VERIFIED PLAYWRIGHT CODE)

**Source**: `.cursor/rules/phase2_script.mdc` § Structure for Each Step, § CRITICAL: Verified Code Requirement

- **Rule**: Each action step must include VERIFIED PLAYWRIGHT CODE, How verified, and Wait for. See phase2_script.mdc for full rule.
- **Check**: In each `script.md`, ensure every action step has a VERIFIED PLAYWRIGHT CODE block and verification/wait notes.
- **Report**: Pass if all scripts meet this; Fail with list of scripts/steps missing verified code.

### 2.5 steps.md Expected Result

**Source**: `.cursor/rules/phase1_steps.mdc` § CRITICAL: Validate That the Action Actually Happened, § Expected Result

- **Rule**: Expected Result must state what to assert (e.g. "Event is marked as CANCELLED in Event List"), not only "dialog closes" or "navigates to …". See phase1_steps.mdc for full rule.
- **Check**: Each test's `steps.md` must have an Expected Result section that describes observable outcomes.
- **Report**: Pass/Fail per test with short note.

### 2.6 Wait strategy (no arbitrary waits)

**Source**: `.cursor/rules/phase2_script.mdc` § CRITICAL: Wait Strategy; `.cursor/rules/phase3_code.mdc` § CRITICAL: Wait Strategy

- **Rule**: Event-based waits with long timeouts (30–45s); no arbitrary `wait_for_timeout()` alone for action completion. Small delays (≤500 ms) only for focus/animation when documented. See phase2_script.mdc and phase3_code.mdc for full rule.
- **Check**: In scoped `test.py` (and `script.md` if desired), grep for `wait_for_timeout`. Any call > 500 ms (or without a preceding event-based wait) is a violation unless justified. Allow only ≤500 ms with an "allowed" / "brief" comment.
- **Report**: Pass if no forbidden long waits and event-based waits use long timeouts; Fail with file:line and suggested replacement (event-based wait with long timeout) where useful.

### 2.7 Context / prerequisites consistency (optional)

**Source**: `.cursor/rules/phase1_steps.mdc` (context, Prerequisites, Returns)

- **Rule**: Docstrings and steps.md should agree on what is saved to context and what prerequisites (from context) are required. See phase1_steps.mdc for full rule.
- **Check**: For tests that pass context (e.g. schedule_event → view_event), ensure steps.md and test docstring match saved/consumed context.
- **Report**: Pass/Fail with short note; can be "N/A" for tests with no context chain.

### 2.8 Matter entity name agnosticism

**Source**: `.cursor/rules/project.mdc` § Matter Entity Name Agnosticism

- **Rule**: Tests must NOT hardcode a single matter entity label in locators or assertions; use regex, positional selectors, or `tests/_params` (ADD_MATTER_TEXT_REGEX). See project.mdc § Matter Entity Name Agnosticism for full rule.
- **Check**: In each resolved test (and related _functions), grep for hardcoded entity-specific strings: literals like "Properties", "Delete properties?", "Add property", or "1 SELECTED OF \d+ PROPERTIES" as the only match. Allowed: positional selectors; regex like `r"1 SELECTED OF \d+"`, `r"Delete .+\?"`; ADD_MATTER_TEXT_REGEX; docstrings that mention entity names as examples.
- **Report**: Pass if no forbidden hardcoded entity-only locators; Fail with file:line and offending string.

### 2.9 No retries for actions

**Source**: `.cursor/rules/project.mdc` § Cross-Cutting Execution Principles; `.cursor/rules/phase3_code.mdc` § No Retries for Actions

- **Rule**: Do not retry user actions; wait for readiness, then act once. No retry loops for clicks, fills, or navigation. See project.mdc § Cross-Cutting Execution Principles for full rule.
- **Check**: In each resolved test, grep for `retry|retries|for attempt in range|Retrying:` in `test.py` and `script.md`. Exclude infrastructure-only retries if documented; all user-action retries are violations.
- **Report**: Pass if no user-action retry loops; Fail with file:line and violation.

### 2.10 Test cleanup and teardown

**Source**: `.cursor/rules/project.mdc` § Test Cleanup Rule

- **Rule**: Category must leave minimal leftover objects; setup-created → teardown; test-created → later test or teardown; cancel/mark inactive when delete not possible; clear context after deletion. See project.mdc § Test Cleanup Rule for full rule.
- **Check**: For each category (or resolved scope): (1) If `_setup` exists, check `_teardown` deletes setup-created objects; (2) For tests that create objects, check corresponding delete/cancel test or teardown; (3) Context variables cleared after deletion; (4) Cancellation documented where applicable. Read `_setup`/`_teardown` steps.md and test.py; read `_category.yaml` for order.
- **Report**: Per-category table: Category | Setup objects | Teardown cleanup | Test sequence cleanup | Context cleared | Status (Pass/Fail/N/A + notes). Pass if no setup OR setup objects cleaned in teardown; all create tests have delete/cancel or teardown cleanup; context cleared. Fail if objects created but never cleaned. N/A if no object creation.

### 2.11 No fallbacks for detection

**Source**: `.cursor/rules/project.mdc` § Cross-Cutting Execution Principles; `.cursor/rules/phase3_code.mdc` § No Fallbacks for Detection

- **Rule**: One condition per step to detect readiness or success; no try/except fallbacks or alternate locators for the same condition. See project.mdc § Cross-Cutting Execution Principles for full rule.
- **Check**: In each resolved test, grep for `fallback|try:.*except|except.*continue` and read `test.py` and `script.md` for "try locator A then locator B" or documented "Fallback: …" for detection. Exclude try/except that only wrap infrastructure if documented.
- **Report**: Pass if no fallback detection in scoped files; Fail with file:line and violation.

### 2.12 Timeout means failure

**Source**: `.cursor/rules/project.mdc` § Cross-Cutting Execution Principles; `.cursor/rules/phase3_code.mdc` § No Fallbacks for Detection / Timeout Means Failure

- **Rule**: If a wait times out, the test must fail and stop; never catch a timeout and continue. See project.mdc § Cross-Cutting Execution Principles for full rule.
- **Check**: In each resolved test, grep for `try:|except|TimeoutError|wait_for.*timeout` in `test.py` and `script.md`. Look for try/except that wraps a wait and continues (e.g. "except: continue", "except TimeoutError: pass").
- **Report**: Pass if no timeout-swallowing or continue-after-timeout; Fail with file:line and violation.

---

## 3. Report format

Produce a single validation report.

1. **Header**
   - Date and scope (list of resolved test paths or category paths).
   - Optional: one-line summary (e.g. "12 rule areas, X Pass, Y Fail").

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
   | 9. No retries for actions | ✅ Pass / ❌ Fail | … |
   | 10. Test cleanup and teardown | ✅ Pass / ❌ Fail / N/A | … |
   | 11. No fallbacks for detection | ✅ Pass / ❌ Fail | … |
   | 12. Timeout means failure | ✅ Pass / ❌ Fail | … |

3. **Per-rule sections**  
   For each rule (1–12), add a section with:
   - Rule (one sentence) and source (rule file § section).
   - Check performed (what you grepped/read).
   - Result: Pass or Fail (or N/A where applicable).
   - If Fail: file paths, line numbers or step names, and concrete violations (and for wait strategy, suggested event-based fixes where useful).
   - For rule 2.10 (cleanup): Include per-category table showing setup objects, teardown cleanup, test sequence cleanup, and context clearing status.
   - For rules 2.11 and 2.12: Include file:line and concrete violation when Fail.

4. **Files to update (optional)**  
   If any Fail: list files that should be updated and what to change briefly.

---

## 4. Execution steps

1. **Resolve scope** from user input (categories and/or test names); list all test directories.
2. **Read rule definitions** from `.cursor/rules/` as needed (project.mdc, phase1_steps.mdc, phase2_script.mdc, phase3_code.mdc) to apply the checks exactly.
3. **Run each check** (grep, file reads) over the resolved test list.
4. **Fill the summary table** and write each numbered rule section with Pass/Fail and details.
5. **Do not modify** test or script files unless the user explicitly asks to fix violations; this command is **validation and reporting only**.

---

## 5. Example invocations

- **Validate one category**: "Validate scheduling/events" → resolve all tests under `tests/scheduling/events/` (including `_setup`), run all rules, output report.
- **Validate specific tests**: "Validate Schedule Event and Cancel Event" → resolve to those test folders, run all rules, output report.
- **Validate multiple categories**: "Validate scheduling/events and clients" → resolve all tests under both category paths, run all rules, output report.
- **Validate everything**: "Validate all tests" or "Validate" with no target → resolve all tests under `tests/` (excluding `_functions` unless requested), run all rules, output report.
