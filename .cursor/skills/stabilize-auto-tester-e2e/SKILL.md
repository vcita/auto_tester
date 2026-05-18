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
5. Fix the root cause with the smallest stable change.
6. Compile edited Python files with `python -m py_compile`.
7. Run lints for edited files.
8. Rerun the same focused scope without `--headless` unless the user asks otherwise.
9. Update health files only from real runner output.

## Setup Data

Prefer API setup for prerequisites that are not the feature under test:

- Create clients, services, and other required records through API when existing patterns are available.
- Store created data in `context` with names the tests already use.
- Keep UI coverage focused on the category behavior being tested.

For auto-account runs, use runner-provided context:

- `context["auto_account"]`
- `context["base_url"]`
- `context["api_base_url"]`
- `context["username"]`
- `context["password"]`

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

## Validation Output

Report the final result with:

- Command run.
- Pass/fail count.
- Runtime.
- Key timing change, if optimization was requested.
- Remaining risk or instability, if any.

