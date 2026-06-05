---
name: stabilize-auto-tester-e2e
description: Stabilize auto_tester E2E categories and subcategories by investigating health files, heal requests, setup bottlenecks, flaky Playwright selectors, and validation runs. Use when fixing unstable tests, reducing category runtime, running health checks, or when the user asks to stabilize an auto_tester category or subcategory.
---

# Stabilize Auto Tester E2E

## Workflow

1. Identify the target scope: category, subcategory, or single test folder under `tests/`.
2. Read the relevant `_category.yaml`, `steps.md`, `script.md`, `test.py`, and recent heal requests.
3. Run the smallest useful command first:
   - Single test when debugging one failure.
   - Subcategory when validating related flows.
   - Full category only after focused fixes pass.
4. Classify failures before editing:
   - Locator or visibility issue.
   - Data/setup issue.
   - Timing/wait issue.
   - Product state issue, such as an action no longer available after payment.
   - Infrastructure issue.
5. When stabilizing migrated automation-js coverage, run the original automation-js test or scenario when it is runnable.
   - Use the old run to compare UI paths, helper behavior, generated data, popups, tabs, and expected assertions.
   - If the new test gets stuck or the correct UI action is unclear, pause and ask the user for a hint on what to press, a photo, a screenshot, or any other clue that can reveal the intended path.
6. Fix the root cause with the smallest stable change.
7. Compile edited Python files with `python -m py_compile`.
8. Run lints for edited files.
9. Rerun the same focused scope without `--headless` unless the user asks otherwise.
10. Update health files only from real runner output.
11. Close out without asking. When stabilization is validated, always commit + push the fix on its `VCITA2-XXXX` branch and open/update the PR, then — if the stabilized scope is migrated from automation-js — update the migration coverage tracker (via `update-migration-coverage-tracker`) with the new status, runtime, and stability evidence. These closeout steps carry standing approval; run them automatically and report links. Pause only for a genuine blocker (push rejected, PR conflict, missing tracker credentials).
12. After any stress test completes, verify all status artifacts before reporting done:
   - Check `git diff` for every related `_category.yaml` and `_health.json`.
   - Confirm the parent category and every tested subcategory have the expected `stability` block.
   - Do not rely only on the runner's final summary; full-category runs may stamp the parent category without stamping each subcategory file.
   - Preserve existing YAML comments and formatting when adding missing stability blocks manually from real 10/10 output.
   - If the runner rewrites `_category.yaml`, keep the real stability result but restore comments and indentation before committing.
   - If waits, timeouts, navigation behavior, or retry logic changed after a stress run, rerun stress before trusting existing `stable` metadata.

## Setup Data

Prefer API setup for prerequisites that are not the feature under test:

- Create clients, services, and other required records through API when existing patterns are available.
- Store created data in `context` with names the tests already use.
- Keep UI coverage focused on the category behavior being tested.
- Never convert a UI action to an API call when that UI action is part of the tested scope or the reusable function's stated objective.
- If a UI cleanup function exists to cover a user flow, stabilize that UI flow instead of bypassing it through an API shortcut.

For auto-account runs, use runner-provided context:

- `context["auto_account"]`
- `context["base_url"]`
- `context["api_base_url"]`
- `context["username"]`
- `context["password"]`

## Scope And Quality Guardrail

For every stabilization change:

- Re-check `steps.md`, `script.md`, and `test.py` together.
- Confirm no user-facing assertion, setup path, edge case, or validation intent was removed.
- Confirm no user-facing UI action was replaced by an API call when that action is part of the declared test/function scope.
- If an assertion is removed as redundant, document which remaining assertion preserves the same behavior coverage.
- Do not mark a test stable if stability was achieved by reducing scope or weakening assertions.
- Do not mark a test stable if stability was achieved by bypassing the UI path that the test is intended to validate.
- Include scope/quality preservation in the final report.

## Selector Strategy

Follow `prefer-data-qa-selectors` when editing Playwright tests.

If stable `data-qa` selectors are missing:

1. Prefer roles and accessible names.
2. Anchor action menus to nearby stable visible actions.
3. Avoid global `md-menu` or last-button selectors when side panels also contain menus.
4. Use screenshots or diagnostic assertion messages to confirm what Playwright can see.
5. Remove noisy diagnostics after the selector is stable.

## Timing Strategy

Do not shorten waits blindly. First determine whether runtime is caused by:

- Real UI work.
- Fixed sleeps.
- Repeated navigation.
- Setup creating data through UI.
- Waiting for a condition that never becomes true.

Reduce runtime by removing avoidable setup work or unnecessary fixed waits. Keep explicit waits around real UI transitions.

When enforcing the 5-second wait policy:

- Pass an explicit 5-second `timeout` to `page.goto(...)`; otherwise Playwright can use its default navigation timeout.
- Cap explicit element, URL, dialog, loader, and polling waits at 5 seconds.
- If a 5-second cap exposes flakiness, investigate the readiness signal, selector, setup data, or product behavior instead of increasing the timeout.
- After changing timeout caps, rerun the relevant stress test and update/stamp stability only from that final run.

## Reduce Waits And Duration (Without Scope Or Quality Loss)

Treat lower per-test waits and total runtime as a goal on every change, but never reduce scope or quality to get there:

- Remove avoidable work first (fixed sleeps, redundant navigation, repeated logins, UI setup that can be API setup) before touching real UI-transition waits.
- Keep waits as explicit condition waits on real readiness signals, capped per the wait policy in `Timing Strategy`.
- Preserve every assertion, setup path, edge case, and in-scope UI action per the `Scope And Quality Guardrail`; do not weaken selectors or bypass the tested UI path for speed.
- If a speedup would cost scope or quality, do not apply it; surface the trade-off in the final report.

## Pre-PR Wait Audit (Mandatory)

Immediately before creating the PR, re-scan every edited `test.py` and helper one more time for wasted time, and fix or explicitly justify each finding:

- **Timeouts past the 5s cap**: flag any `timeout=`/wait above 5 seconds (`page.goto`, `wait_for`, `expect`, locator waits, and polling deadlines). Lower it to ≤5s per the `Timing Strategy`, or document in `changelog.md` why a longer bounded poll is genuinely required (asynchronous product indexing or eventual consistency only — never to mask a flaky selector/setup).
- **More than 2 retries**: flag any retry/reload loop that runs more than 2 retries. Reduce it to ≤2, or justify the bounded count against a real async readiness signal.
- **Avoidable duration**: remove leftover fixed sleeps, redundant navigation/reloads, repeated logins, and UI setup that can be API setup for out-of-scope prerequisites.

If this audit changes any wait, timeout, or retry logic, rerun the relevant `stress_test` and re-stamp stability from that final run before opening the PR (consistent with the `Timing Strategy` rule on re-running stress after timeout/retry changes). Never trade scope or quality for speed; surface the trade-off instead.

## Infrastructure Flakes

- Treat account-creation HTTP 5xx responses as transient infrastructure; retry once, then fail normally if the retry also fails.
- Keep fatal authentication/configuration errors non-retryable.

## Validation Output

Report the final result with:

- Command run.
- Pass/fail count.
- Runtime.
- Key timing change, if optimization was requested.
- Remaining risk or instability, if any.

