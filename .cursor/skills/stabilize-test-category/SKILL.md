---
name: stabilize-test-category
description: Stabilizes an auto_tester category by preserving full test scope, running 10 consecutive headless stress-test iterations, applying only quality-improving fixes, and stopping for review after one category reaches stable. Use when the user asks to stabilize a category, mark tests stable, run category stress tests, or improve flaky auto_tester tests without reducing coverage.
---

# Stabilize Test Category

## Core Rule

A category can be considered `stable` only when the full category runs headless and passes 10 consecutive stress-test iterations.

```bash
.venv/bin/python main.py stress_test --categories <category> --iterations 10 --headless
```

## Guardrails

- Never remove, hide, skip, draft, rename, or narrow existing tests or subcategories to make the category pass.
- Never weaken assertions or replace meaningful validations with smoke checks.
- Only make changes that preserve or improve quality, scope, determinism, cleanup, selector reliability, waits, or setup.
- Stabilize one category at a time. After one category reaches `stable`, stop and report results for user review before moving to the next category.
- If a run passes with fewer than 10 iterations, do not treat it as stable.

## Workflow

1. Verify the working tree and identify the category to stabilize.
2. Read `tests/<category>/_category.yaml` and nested `_category.yaml` files to confirm the current full scope.
3. Check for hidden, disabled, draft, or excluded tests before running. Do not use those mechanisms as a stabilization shortcut.
4. Run the full category stress test headless for 10 iterations.
5. If it passes 10/10, verify `tests/<category>/_category.yaml` was stamped with `stability.status: stable`.
6. If it fails, inspect the failing test, logs, screenshots, and heal requests.
7. Apply the smallest quality-preserving fix.
8. Re-run focused checks as needed, then repeat the full 10-iteration headless stress test.
9. When the category is stable, summarize the diff, test result, and any remaining risk. Stop before touching another category.

## Acceptable Fixes

- Improve waits around real readiness conditions.
- Prefer stable `data-qa` selectors, then semantic selectors, then text/CSS fallbacks.
- Make test data unique and deterministic.
- Improve cleanup so repeated stress runs do not leak state.
- Strengthen setup and teardown without skipping behavior under test.
- Add assertions that verify actual persisted UI or data state.

## Unacceptable Fixes

- Moving failing tests to hidden folders.
- Removing subcategories from `execution_order`.
- Marking tests disabled, skipped, draft, or blocked to earn stability.
- Replacing flow validation with only navigation or toast checks.
- Hardcoding success when the UI did not prove the behavior.
- Changing the product scenario being tested to a narrower scenario without explicit user approval.
