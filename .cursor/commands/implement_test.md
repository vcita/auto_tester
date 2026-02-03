# Implement Test

Build a complete test following the **3-phase methodology** (steps → script → test.py). This command defines the **implement protocol** (phases, order, validation). What makes a good test (no retries, real user actions, wait strategy, assertions, etc.) is defined in the rules files—refer to them instead of repeating.

**Rules to follow:**
- **Build process and checklist:** `.cursor/rules/build.mdc`
- **Cross-cutting principles (no retries, single detection, timeout):** `.cursor/rules/project.mdc` § Cross-Cutting Execution Principles
- **Real user actions / navigation:** `.cursor/rules/project.mdc` § Real User Actions Rule
- **Matter entity agnosticism:** `.cursor/rules/project.mdc` § Matter Entity Name Agnosticism
- **Checking similar tests / function reuse:** `.cursor/rules/project.mdc` § Check Similar Tests When Building or Healing, § Function Reuse Rules
- **How to write steps/script/code:** `.cursor/rules/phase1_steps.mdc`, `phase2_script.mdc`, `phase3_code.mdc`

---

## URLs and Config

Use **base_url + "/login"** from config.yaml (target.base_url); never hardcode the host. Credentials from config.yaml target.auth. New test user: `python main.py create_user`. See **build.mdc** § CRITICAL: Use base_url from config.yaml and § Configuration.

---

## PHASE 1: Create steps.md

1. **Check existing functions and similar tests** — Read `tests/_functions/_functions.yaml`; use `Call: function_name` when a function matches. Search for tests that do the same or similar user flow; reuse their flow and patterns. See **project.mdc** § Function Reuse Rules and § Check Similar Tests When Building or Healing.
2. **Research** the feature (e.g. vcita support / knowledge center). See **build.mdc** § CRITICAL: Research Phase - Knowledge Center.
3. **Write human-readable steps** (WHAT to do, not HOW). See **phase1_steps.mdc** for content, structure, and examples.

**Do not write script.md or test.py until steps.md is complete.** See **project.mdc** § CRITICAL: Strict Phase Order.

---

## PHASE 2: Create script.md via MCP Exploration

1. **Align with similar tests** — Use the same locator and flow patterns as any similar working test from Phase 1; document in script.md when a locator matches test X or function Y. See **project.mdc** § Check Similar Tests When Building or Healing.
2. **Explore with Playwright MCP** — Validate each step; document LOCATOR DECISION tables and **VERIFIED PLAYWRIGHT CODE** from MCP. See **phase2_script.mdc** and **build.mdc** § Step-by-Step Build Process (Explore with MCP, Generate script.md).
3. **UI interaction patterns** — Hover before hidden buttons, inspect DOM with MCP, complete full flow in MCP before updating any code. Matter entity: use regex/positional selectors; for "Add &lt;entity&gt;" use `tests._params.ADD_MATTER_TEXT_REGEX`. See **build.mdc** § Key UI Interaction Patterns and **project.mdc** § Matter Entity Name Agnosticism.

**Do not generate test.py until the entire flow works in MCP.** See **build.mdc** § CRITICAL: Complete the Full Action During Exploration.

---

## PHASE 3: Generate test.py

1. **Copy VERIFIED PLAYWRIGHT CODE exactly from script.md** — Do not modify or improve locators. See **phase3_code.mdc** (copy from script, use verified code only).
2. **Wait strategy** — Use event-based waits with long timeouts (30–45s); do not use `wait_for_timeout()` alone for action completion. See **phase2_script.mdc** § CRITICAL: Wait Strategy and **phase3_code.mdc** § CRITICAL: Wait Strategy.
3. **No retries for actions** — Wait for readiness, then act once. See **project.mdc** § Cross-Cutting Execution Principles.

**Generate test.py only after the full flow has been validated in MCP.** See **build.mdc** § CRITICAL: Complete the Full Action During Exploration.

---

## PHASE 3.5: Validate Test Adheres to Rules (Before Running)

**After generating test.py but before running, ensure the test adheres to project and phase rules.**

- **No `page.reload()` or `page.goto()` to internal URLs** — Only entry point (e.g. login) is allowed. Navigation must use UI (menus, buttons, links). See **project.mdc** § Real User Actions Rule and **build.mdc** § CRITICAL: Real User Actions Only, § CRITICAL: No Fallbacks or Alternative Flows.
- Check test.py, script.md, and steps.md for violations. If any: fix (UI-based navigation), re-validate with MCP if needed, then proceed to Phase 4. Exception: documented **product bug workaround** (rare). See **phase3_code.mdc** for code-level rules.

---

## PHASE 4: Run and Validate

**Always use the runner.** Category is the atomic test unit:

```bash
python main.py run --category <category_name>
```

The runner handles captcha bypass, timeouts, video recording, and screenshots. Fix any failures until the category passes. On failure: check console output, screenshots in `_runs/<run_id>/`, and video recordings. See **phase3_code.mdc** § CRITICAL: No Standalone Test Blocks.

**If you fix anything in this phase (selectors, timing, navigation), re-run PHASE 3.5 (Validate Test Adheres to Rules) before PHASE 5.**

---

## PHASE 5: Update changelog.md

Add an entry to `tests/{category}/{test_name}/changelog.md` following the format in **build.mdc** § 6. Update changelog.md (e.g. date, Initial Build, phases touched, summary of what was built).

---

## Continue Until Complete

**Work through all phases until the test is implemented and validated.** Do not stop unless you hit a genuine blocker or need information only the user can provide. See **build.mdc** § CRITICAL: Continue Until Complete and § Implementation Checklist.

- **Continue when:** next step is clear (even if tedious), pattern is clear from similar tests, or you need more MCP exploration or file generation.
- **Stop only when:** genuine blocker with no path forward, user input required, product bug needs user decision, or **all phases are complete for all tests** in the category.

**Before stopping, verify:** steps.md, script.md, and test.py created; Phase 3.5 validation done; tests run and pass (Phase 4); changelog.md updated (Phase 5). If any item is incomplete and you know how to do it, continue. See **build.mdc** § CRITICAL: Run the Test Before Marking Complete and § Quality Checklist.
