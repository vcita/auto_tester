---
name: create-test-from-template
description: End-to-end skill that reads a filled auto_tester Confluence design template and produces a fully stable, stress-tested test. Covers Phase 1 (steps.md), Phase 2 (script.md via Playwright MCP), Phase 3 (test.py), focused run, heal loop, stress test, and Confluence update. Use when a design template page is ready and the user says "build the test", "create test from template", or pastes a Confluence URL.
---

# Create Test From Template

Single command that takes a filled Confluence design template and delivers a stable, stress-tested auto_tester test with zero manual steps in between.

**Invoke as:** `/create-test-from-template <confluence_page_url_or_id>`

---

## Phase 0 — Fetch and Validate the Template

1. Extract the page ID from the URL (numeric segment after `/pages/`) or use the ID directly.
2. Fetch the page using the Atlassian Rovo MCP:
   - Tool: `mcp__claude_ai_Atlassian_Rovo__getConfluencePage`
   - `cloudId`: `myvcita.atlassian.net`
   - `contentFormat`: `markdown`
3. Validate that the following fields are **not** `TBD`:
   - Section 1: Flow name, Target category/subcategory
   - Section 3: User role, Account type
   - Section 5: At least one user action row with a real action and expected result
4. If any required field is still `TBD`, stop and list exactly which fields need filling before the skill can proceed. Do not guess or infer missing values.
5. Check whether Section 5 rows contain inline screenshots (Confluence image attachments embedded in the table). Note their presence — screenshots are optional but dramatically speed up Phase 2.

---

## Phase 1 — Scaffold the Test (steps.md)

Read `.cursor/rules/phase1_steps.mdc` and `.cursor/skills/generate-subcategory/SKILL.md` before writing any files.

### Determine the test path

Parse "Target category/subcategory" from Section 1. Map it to a folder path:

```
tests/<team>/<domain>/<subcategory>/<test_name>/
```

- Derive `<team>` using `.cursor/skills/team-taxonomy.md` (Confluence squads page pageId `2615410911` is the source of truth).
- Use the flow name (snake_case) as `<test_name>`.
- If the subcategory folder does not exist, create it with `_category.yaml` following the `generate-subcategory` skill conventions.

### Write steps.md

Translate Section 5 (User Flow and Expected Results table) into `steps.md`:

- Each row in the table → one numbered step + its expected result check.
- Use the "User action" column as the step text (WHAT, not HOW).
- Add a verification step after every state-changing action using the "What should we assert?" column.
- Pull prerequisites from Section 3 (user role, account, feature flags).
- Pull data setup from Section 4 (what needs to exist before the flow starts).
- Use `Call: login` for the login step (do not re-describe it).
- Apply all rules from `phase1_steps.mdc`: no selectors, no code, one action per step, real-data assertions only.

Write `steps.md` to the test folder. Do not create `script.md` or `test.py` yet.

### Write changelog.md

```markdown
## <YYYY-MM-DD> — Initial creation from Confluence template
- Created from: <confluence_page_url>
- Jira task: <jira_task from Section 1>
- Flow: <flow_name>
```

---

## Phase 1.5 — Choose Target Environment and Create Exploration Account

**Actively ask the user before starting exploration:**

> "Which fenv should I run the Phase 2 browser exploration on?
> **Recommended: `integration`** (`https://app.meet2know.com`).
> Or enter a personal fenv name (e.g. `aviv` → `https://app-aviv.external.int-eks.vchost.co`).
> Type the fenv name or press Enter to use `integration`."

Wait for the user's answer. Do not proceed to Phase 2 until you have a confirmed fenv name.

**Resolve the `app_base_url`** from the fenv name (mirrors `src/runner/env_config.py`):

| Fenv | App URL |
|---|---|
| `integration` | `https://app.meet2know.com` |
| `production` | `https://app.vcita.com` |
| `<name>` (personal fenv) | `https://app-<name>.external.int-eks.vchost.co` |

**Create an exploration account** on the target fenv using the runner's auto-account pattern (`auto.<category>.<timestamp>@vcita.com`, password `vcita123`):

```bash
python main.py run --category <team>/<domain>/<subcategory>/<test_name> --env <fenv>
```

This creates a fresh account on the target fenv. The account credentials are written to `.context/<Team>_context.json` under `auto_account`. Read that file after the runner exits and pass the `email`, `password`, and `app_base_url` as the login context for the test-explorer.

> **Note:** `run` will fail at test execution (test.py does not exist yet) — that is expected. The account is already created before tests run. Ignore the test failure; use the account from the context file.

---

## Phase 2 — Explore the UI and Write script.md

Delegate to the **test-explorer** subagent (`.cursor/agents/test-explorer.md`).

Pass to the subagent:
1. The path to the newly written `steps.md`.
2. Any similar working test in the same subcategory or domain (grep for an existing `script.md` nearby that covers the same entry page — pass its path so the explorer reuses committed locators).
3. The `app_base_url` resolved in Phase 1.5 (e.g. `https://app.meet2know.com`) — use this as `base_url` for all navigation. Do **not** use the default from `config.yaml`.
4. The exploration account credentials from `.context/<Team>_context.json` (`auto_account.email` and `auto_account.password`).
5. **Screenshots from the template** (if any were found in Phase 0): list the steps that have screenshots and describe what each screenshot shows. The explorer must use these as primary visual references when locating UI elements at those steps instead of exploring blindly.
6. Data context from Section 4: what records already exist (created via API/setup) and what their names/IDs are in the live test account.

The test-explorer returns: `script.md` path + a short summary of discovered locators and any blockers. It must complete the full flow (including the confirmation/result screen) before returning.

If the explorer reports a blocker (e.g., a UI path that does not match the template's expected flow), **pause and show the discrepancy to the user** before continuing. Do not invent a workaround silently.

---

## Phase 3 — Implement test.py

Delegate to the **test-codegen** subagent (`.cursor/agents/test-codegen.md`).

Pass: the `script.md` path and the `steps.md` path.

The codegen subagent returns: `test.py` path + a short summary.

After it returns:
- Compile: `python -m py_compile tests/<path>/test.py`
- If compile fails, fix inline (do not re-delegate) and re-compile.

---

## Phase 4 — Focused Run

Run the test without headless so the flow is visually verifiable. Use the same fenv chosen in Phase 1.5:

```bash
python main.py run --category <team>/<domain>/<subcategory>/<test_name> --env <fenv>
```

**On pass:** proceed to Phase 5.

**On failure:** enter the Heal Loop (below). Maximum 3 heal cycles. If still failing after 3, stop, report the last error and screenshot path to the user, and ask for guidance.

### Heal Loop

For each failure cycle:
1. Read the error output and the failure screenshot from `snapshots/`.
2. Apply the smallest fix that targets the root cause:
   - Locator issue → update selector in `script.md` and `test.py`.
   - Timing issue → add a `browser_wait_for` condition.
   - Flow mismatch → compare against `steps.md` and correct the code path.
3. Re-compile and rerun.
4. Log the fix in `changelog.md` with the date and a one-line reason.

---

## Phase 5 — Visual E2E Verification

Run the test without headless and observe the browser (same fenv as Phase 1.5):

```bash
python main.py run --category <team>/<domain>/<subcategory>/<test_name> --env <fenv>
```

Confirm that:
- The visible flow matches Section 5's step-by-step description.
- Assertions check real data/state (not just toasts or redirects).
- If the template had screenshots, compare each screenshot to the actual browser state at that step.

If the visible flow diverges from the template design, update `steps.md` and propagate the change through `script.md` and `test.py` following `sync-steps-with-script-changes.mdc`. Log the delta in `changelog.md`.

---

## Phase 6 — Stress Test

```bash
python main.py stress_test --categories <team>/<domain>/<subcategory>/<test_name> --iterations 10 --env <fenv>
```

**Passing criteria:** result says `STABLE` or `stable` with 10/10 runs.

**On flaky result:** read the failure detail, identify the instability root cause, fix it (selector, wait, data cleanup), re-run Phase 4 focused run to confirm the fix, then rerun stress test. Repeat until stable or until 3 stabilization cycles are exhausted (then pause and report).

After a stable stress result, verify the `_health.json` and `_category.yaml` stability blocks were written correctly — do not rely on the runner summary alone.

---

## Phase 7 — Update Confluence

Update the template page's **Section 7 (Build and Validate)** and **Final Test Details** with actual results.

Use `mcp__claude_ai_Atlassian_Rovo__updateConfluencePage` — preserve the full page body; only replace the TBD cells in the two sections below.

### Section 7 rows to fill

| Step | Required result | Actual result to write |
|---|---|---|
| Prepare test design | steps.md matches agreed flow | `Pass — steps.md at <path>` |
| Explore the flow | Flow path is clear before coding | `Pass — script.md at <path>` |
| Reuse existing code | Existing helpers reused | `Pass` / `No reusable helpers found` |
| Implement the test | Test implemented | `Pass — test.py at <path>` |
| Code check | No compile errors | `Pass` |
| Focused run | Pass | `Pass` |
| Visual E2E review | Flow matches design | `Pass` / `Delta: <note>` |
| Stability run | 10/10 and STABLE | `<actual stress result>` |
| Evidence review | No unresolved issue | `Pass` / `<open issue if any>` |

### Final Test Details to fill

| Field | Value |
|---|---|
| Final test path | `tests/<team>/<domain>/<subcategory>/<test_name>` |
| Stress test result | `Stable` |
| PR link | (leave TBD — user commits separately) |
| Notes for future maintainers | Any selector caveats, data dependencies, or env exceptions found during build |

---

## Rules That Always Apply

- Read `.cursor/rules/build.mdc` before starting Phase 2 delegation.
- Never skip a phase. `steps.md` → `script.md` → `test.py`. No code without a verified script.
- Every state-changing action needs a real-data assertion, not a toast check.
- Real user actions only: no direct API calls for steps that are under test.
- Log every change in `changelog.md`.
- Never commit run artifacts (`_health.json`, `runs_index/`, `_runs/`) — stage only source files.

---

## Using Screenshots From the Template

When the template's Section 5 rows contain inline screenshots (the product person walked through the UI and pasted a screenshot per step), treat them as primary design input for Phase 2:

- Name each screenshot by its step number (e.g., "Step 2 screenshot").
- Pass the screenshot description + the step text together to the test-explorer subagent.
- The explorer must look at each screenshot before deciding which selector to target — the screenshot shows the exact UI state at that moment, including visible labels, buttons, and layout.
- A step with a screenshot should require significantly less blind Playwright exploration than a step without one.

If the template has no screenshots, the test-explorer relies entirely on live Playwright MCP exploration (standard Phase 2 behavior).

---

## Reporting

After the skill completes (or stops on a blocker), report:

```
✓ steps.md:    tests/<path>/steps.md
✓ script.md:   tests/<path>/script.md
✓ test.py:     tests/<path>/test.py
✓ Focused run: Pass
✓ Stress test: 10/10 STABLE
✓ Confluence:  Section 7 and Final Test Details updated
  <url>
```

Or, on a blocker:

```
⚠ Stopped at Phase <N>: <reason>
Last artifact: <path>
Next step needed from you: <clear ask>
```
