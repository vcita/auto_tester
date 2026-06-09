# Heal Test

Fix a failing test by following the **heal protocol** below. This command defines the **process** (steps, order, validation). What makes a good test (no retries, real user actions, wait strategy, assertions, etc.) is defined in the rules files—refer to them instead of repeating.

**Rules to follow:**
- **Heal process and checklist:** `.cursor/rules/heal.mdc`
- **Cross-cutting principles (no retries, single detection, timeout):** `.cursor/rules/project.mdc` § Cross-Cutting Execution Principles
- **Real user actions / navigation:** `.cursor/rules/project.mdc` § Real User Actions Rule
- **Matter entity agnosticism:** `.cursor/rules/project.mdc` § Matter Entity Name Agnosticism
- **Checking similar tests:** `.cursor/rules/project.mdc` § Check Similar Tests When Building or Healing
- **How to edit steps/script/code:** `.cursor/rules/phase1_steps.mdc`, `phase2_script.mdc`, `phase3_code.mdc`

---

## Protocol: Must End with Successful Runner Run

**`/heal_test` is not complete until the relevant test/category is run with the runner and passes.** Run the category (e.g. `python main.py run --category scheduling/appointments`). If it fails again, continue healing (retry up to 5 times or mark UNRESOLVED). Healing is done only when the runner reports pass.

---

## Same Account and URLs for MCP

When debugging with MCP, use the **same account** that ran the failed test (credentials from heal request / `config.yaml` target.auth). Different account → different data/UI and hides the real bug. Use **base_url + "/login"** from config; log out first if MCP is already logged in as someone else. New test user: `python main.py create_user`. See **heal.mdc** § MANDATORY THIRD STEP (Use the SAME account) and § MCP Debugging: Availability and Config.

---

## STEP 1: Understand What Happened

1. **Locate heal request** in `.cursor/heal_requests/` (format: `heal_[test_id]_[timestamp].md`).
2. **Read changelog and analyze screenshot/video** — See **heal.mdc** § MANDATORY FIRST STEP (Read the Changelog) and § MANDATORY SECOND STEP (Screenshot AND Video Analysis). Look at the failure screenshot (path in heal request under "## Screenshot") before any fix or theory.
3. Read error message and current test files (test.py, script.md, steps.md).
4. **Check similar tests** — See **project.mdc** § Check Similar Tests When Building or Healing. Reuse patterns from tests/functions that exercise the same UI flow or product area.
5. **Document your initial understanding** — but you must verify with MCP; do not fix from logs alone.

Regardless of what the changelog shows, proceed to MCP debugging (Step 2).

---

## STEP 2: Research with Playwright MCP (MANDATORY)

**You must use Playwright MCP to simulate the test and observe what actually happens.** Do not skip this even if you think you understand the issue. See **heal.mdc** § MANDATORY THIRD STEP (Debug with MCP) and § 3. Step-by-Step Debugging with MCP.

- **Same account:** Log in with credentials from heal request/config; verify visible user matches before reproducing steps. See heal.mdc § Use the SAME account as the failed test.
- **Wait strategy:** Use state-based waits capped at 5 seconds (`timeout=5000`); do not add retry loops or raise timeouts to mask flakiness. See **heal.mdc** § CRITICAL: Wait Strategy When Healing and **project.mdc** § Cross-Cutting Execution Principles.
- **UI interaction patterns:** Hover before hidden buttons, inspect DOM with MCP, complete full flow in MCP before updating code. See **heal.mdc** § 3.5. Key UI Interaction Patterns.
- **Matter entity:** When fixing selectors that refer to matter entity labels, use entity-agnostic patterns. See **project.mdc** § Matter Entity Name Agnosticism.

### 2.1: MCP Has Its Own Browser

Playwright MCP controls **its own** browser. You cannot attach MCP to a browser opened by the Python runner or a debug script. Use `--until-test` to **dump context**; then debug in a **new** MCP browser session using that context. See **heal.mdc** § MCP Uses Its Own Browser.

### 2.2: Get Context with `--until-test`

1. Identify the failing test name from the heal request (e.g. `Events/_setup`, `Events/Schedule Event`).
2. Run:
   ```bash
   python main.py run --category scheduling/events --until-test "Events/Schedule Event"
   ```
3. Runner runs setup and tests before that test, writes **until_test_context.json** to the run dir (next_test, url, title, context), and leaves the browser open for manual debug.
4. **For MCP:** Start a new MCP browser (cannot attach to that open browser). Log in with the same account, then either navigate to the **url** from `until_test_context.json` or re-run the flow using **context** values. Execute the failing test steps one-by-one in MCP and verify.

**Alternative:** If `--until-test` cannot be used, start MCP browser, log in, then replicate the flow from steps.md/script.md using context from the heal request or run artifacts.

### 2.3: Execute Test Step-by-Step in MCP

Execute test steps one-by-one; verify each step visually; document what worked and what failed. **Do not update test code until the full flow succeeds in MCP.** See **heal.mdc** § 3. Step-by-Step Debugging with MCP (checklist and process).

---

## STEP 3: Classify the Issue

Based on MCP observations, determine: **product bug** (system issue) or **test bug** (test issue). See **heal.mdc** § 2. Classify the Issue.

- **Product bug:** Halt immediately. Do not fix the test. Inform the user, document in heal request and run log, create bug report in `.cursor/bug_reports/`, mark test blocked in `_category.yaml`, delete the heal request. See **heal.mdc** § Handling Product Bugs.
- **Test bug:** Document root cause (selector, timing, flow change), what MCP revealed, and a plan for what to change (which files: steps.md, script.md, test.py) and how.

---

## STEP 4: Validate Fix with MCP (Before Code Changes)

**Before changing any code, validate the fix end-to-end in MCP.** Run the full test flow in MCP with the proposed fix (new selectors/flow). Only if the full flow passes in MCP, proceed to update files. If validation fails, return to Step 2 and try a different approach. See **heal.mdc** § 3 (complete entire flow with MCP before updating code).

---

## STEP 5: Fix Files in Correct Order

Update only what is needed, in order: **steps.md → script.md → test.py.** See **heal.mdc** § 4. Update script.md and § 5. Regenerate test.py.

- **steps.md:** Only if test goals or flow changed. See **phase1_steps.mdc**.
- **script.md:** Update VERIFIED PLAYWRIGHT CODE with the code that worked in MCP; update LOCATOR DECISION if selectors changed. See **phase2_script.mdc**.
- **test.py:** Copy VERIFIED PLAYWRIGHT CODE from script.md exactly; add HEALED comments. See **phase3_code.mdc** (copy from script, do not invent locators).

---

## STEP 5.5: Validate Test Adheres to Rules (Before Documenting)

Before updating the changelog, ensure the fixed test adheres to project and phase rules. In particular:

- **No `page.reload()` or `page.goto()` to internal URLs** — only entry point (e.g. login) is allowed. Navigation must use UI (menus, buttons, links). See **project.mdc** § Real User Actions Rule and **phase3_code.mdc** (assertions, no standalone blocks).
- Check test.py, script.md, and steps.md for violations. If any: fix (use UI-based navigation), re-validate with MCP if needed, then proceed to document. Exception: if a reload/goto is a documented **product bug workaround**, document it in changelog and comments (rare).

---

## STEP 5.6: Scope & Quality Guardrail (After the Fix)

Before documenting, verify the fix did not reduce scope or weaken quality versus the pre-heal test:

- Re-check `steps.md`, `script.md`, and `test.py` together; they must agree, and `test.py` must still perform every assertion the docs promise.
- Confirm no user-facing assertion, setup path, edge case, or validation intent was removed to make the test pass.
- Confirm no in-scope UI action was replaced by an API shortcut, and no UI path the test is meant to validate was bypassed. See **project.mdc** § Real User Actions Rule.
- If an assertion was removed as redundant, document in `changelog.md` which remaining assertion preserves the same behavior coverage.
- Do not weaken a selector (role/label/`data-qa` → fragile position/text) just to make it green; prefer the strongest stable selector. See **prefer-data-qa-selectors**.
- Never mark a heal complete if stability was achieved by shrinking scope or weakening assertions.

---

## STEP 5.7: Wait & Duration Audit (After the Fix)

Before documenting, re-scan the edited `test.py` and helpers for wasted time, and fix or explicitly justify each finding:

- **Wasted retries**: flag any retry/reload loop above 2 retries; reduce to ≤2, or justify the bounded count against a real async readiness signal. Never fix flakiness with blind "retry the action" loops. See **heal.mdc** § No Retries for Actions and **project.mdc** § Cross-Cutting Execution Principles.
- **Fixed sleeps**: replace any `page.wait_for_timeout()`/`sleep()` used to wait for an action to complete with an explicit condition wait on a real readiness signal. See **heal.mdc** § CRITICAL: Wait Strategy When Healing.
- **Oversized timeouts**: flag any `timeout=`/wait above the project 5-second cap; lower it to ≤5s, or document why a longer bounded poll is genuinely required (asynchronous product indexing/eventual consistency only). Never fix timing by increasing a timeout.
- **Avoidable duration**: remove redundant navigation/reloads, repeated logins, and UI setup that can be API setup for out-of-scope prerequisites; shorten any action that can be performed faster without losing coverage.
- Never trade scope or quality for speed — if a speedup would cost either, skip it and surface the trade-off.

If this audit changes any wait, timeout, or retry, re-run the category (STEP 7) to confirm it still passes before completing the heal.

---

## STEP 6: Document the Fix

See **heal.mdc** § 6. Update changelog.md for format and examples.

- **changelog.md:** Add entry to `tests/{category}/{test_name}/changelog.md` (date, issue type, phase, reason, error, root cause, fix applied, changes, verified approach).
- **Heal request:** Add "## Healing Result" (issue type, root cause, fix applied, MCP validation, files updated, re-run result). Update **Status** in the heal request file to `fixed` (in `.cursor/heal_requests/`, after header section, before `---`). If unresolved after 5 attempts: add "## Healing Result - UNRESOLVED" and keep status open (groom will mark expired if changelog is newer). If product bug: create bug report, set status to `reported` or leave open for groom.
- **Failed run log:** Document outcome (Healed with summary, or UNRESOLVED with attempts and estimation).

**Status update:** In the heal request file, find or add `**Status**: \`fixed\` | \`reported\` | \`open\`` after the header (e.g. after **Duration**), before the `---` separator.

---

## STEP 7: Validate Fix and Retry if Needed

1. **Run the category** with the runner (e.g. `python main.py run --category scheduling/appointments`) to validate the fix.
2. **If pass:** Healing complete; proceed to Step 8.
3. **If fail again:** Restart from Step 1. Document attempt number. Retry up to 5 times (re-read changelog, re-run MCP, try different approach).
4. **After 5 failed attempts:** Create and run a standalone debug script from `debug_test_skeleton.py` (see **heal.mdc** § Escalation: Standalone Debug Script When Stuck). Then mark heal request UNRESOLVED; add "## Healing Result - UNRESOLVED" with summary, what was tried, debug script findings, and estimation of the issue. Update failed run log accordingly. Do not delete the heal request.
5. **If you clearly identify a product bug or unfixable issue** before 5 attempts: follow product-bug handling (Step 3) or document and inform the user; you may stop early.

---

## STEP 8: Clean Up

Only if the test is fixed and validated by a successful runner run: **delete the heal request** from `.cursor/heal_requests/`. If marked UNRESOLVED, keep the heal request for manual review.

---

## Quality Checklist

Use this to confirm the protocol was followed. For the full list and details, see **heal.mdc** § Quality Checklist.

- [ ] Screenshot analyzed (path in heal request); changelog read
- [ ] Context from `--until-test` (until_test_context.json) or replicated from steps/script; MCP session used same account
- [ ] Full flow executed in MCP before any code change; MCP browser closed when done
- [ ] Issue classified (product bug → halt and report; test bug → fix)
- [ ] Fix validated in MCP (A–Z); files updated in order (steps → script → test.py)
- [ ] Test adheres to rules (no reload/goto to internal URLs; see project.mdc § Real User Actions)
- [ ] **Scope & quality did not decline** - no removed assertions/edge cases, no in-scope UI action swapped for API, no weakened selectors (STEP 5.6)
- [ ] **Wait & duration audit passed** - no wasted retries (≤2), no fixed sleeps for action completion, no timeouts above the 5s cap (or justified), no avoidable duration (STEP 5.7)
- [ ] changelog.md, heal request, and failed run log updated
- [ ] **Category re-run with runner** — pass required for healing to be complete
- [ ] If unresolved after 5 attempts: debug script run and UNRESOLVED documented; heal request kept

---

## Common Issue Patterns

See **heal.mdc** § Common Issues Found During Step-by-Step Debugging for patterns and solutions (e.g. element not found → selector; timeout → wait strategy; wrong value → verify in UI).

---

## Remember

- **Do not guess** — observe with MCP first. See **heal.mdc** for principles (never guess, validate before coding, document everything).
