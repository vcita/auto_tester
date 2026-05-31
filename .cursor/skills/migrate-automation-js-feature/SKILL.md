---
name: migrate-automation-js-feature
description: Migrate legacy automation-js Gherkin feature coverage into auto_tester with zero scope loss, strict mapping, three-phase test artifacts, and stability validation. Use when migrating .feature files, translating automation-js step definitions/page objects/API setup, or creating a migration_mapping.md before implementing auto_tester tests.
---

# Migrate automation-js Feature

## Workflow

1. Identify the `.feature` file or scenario scope to migrate from `automation-js`.
   - If the user names a specific feature, scenario, tag, or domain, migrate that requested scope.
   - If the user does not name a scope, ask them what to migrate or propose candidates without excluding categories by default.
   - Record any known risks in `migration_mapping.md`; do not drop coverage because a flow is complex, flaky, or tagged.
2. Read the full legacy chain before writing code:
   - Feature file scenarios and data tables.
   - Step definitions under `automation-js/steps`.
   - Page objects under `automation-js/pages`.
   - API helpers under `automation-js/api`.
   - Table parsers and context helpers when scenarios use table assertions or `[context.*]`.
3. Run the original automation-js test before or during creation when it is runnable.
   - Use the old run to observe real UI behavior, timing, generated data, popups, tabs, and legacy helper side effects.
   - If the new test gets stuck or the UI path is unclear, pause and ask the user for a hint on what to press, a photo, a screenshot, or any other clue that can reveal the intended path.
   - Use the old run evidence to build the mapping and avoid replacing a legacy UI action with an API shortcut by mistake.
4. Create `migration_mapping.md` before implementation.
   - List every original scenario, action, assertion, setup, and edge case.
   - Map each legacy step to the auto_tester category/subcategory/test structure.
   - Call out any helper/function gaps before coding.
   - Do not write `test.py` until the mapping is complete.
   - Treat `migration_mapping.md` as a local planning artifact. It is important for preventing scope loss, but it should not be committed or included in the PR.
5. Implement in strict auto_tester phase order:
   - `steps.md`: user-facing WHAT, no selectors or code.
   - `script.md`: Playwright-oriented HOW, including locator choices and waits.
   - `test.py`: executable code.
   - `changelog.md`: every creation, fix, and validation-relevant decision.
6. Register the test in `_category.yaml`.
   - Add new subcategories to parent `execution_order` when the parent uses it.
   - Test IDs must match folder names.
7. Validate before calling the migration done.
   - `PYENV_VERSION=3.11.9 python -m py_compile <edited .py files>`
   - `PYENV_VERSION=3.11.9 python main.py list --category <category>`
   - Reference deeply nested isolated subcategories by their full path (e.g. `payments/tips_settings/edit_persist`), not just the leaf name. Confirm the exact path with `python main.py list` before running.
   - Focused run: `PYENV_VERSION=3.11.9 python main.py run --category <category/subcategory> --env integration --headless`
   - Run the migrated scope successfully 3 times with fresh runner state before stress testing.
   - **Hard gate before stress_test**: after those 3 successful runs, re-check `migration_mapping.md`, `steps.md`, `script.md`, and `test.py` against the legacy `.feature`, step definitions, page objects, API helpers, and assertions.
   - Do not start `stress_test` until scope at least matches the legacy test and quality is at least as strong as the legacy test: no removed user-facing assertions, no lost setup/edge-case coverage, no UI action replaced by API when the UI action is in scope, and no weaker selector/wait strategy than the old flow.
   - Stability run only after the hard gate passes: `PYENV_VERSION=3.11.9 python main.py stress_test --categories <category/subcategory> --iterations 3 --env integration --headless`
8. After a successful migration, run the original and migrated tests and report the comparison.
   - Run the migrated auto_tester scope and capture duration, pass/fail count, and command.
   - Run the original automation-js scope and capture duration, pass/fail count, and command.
   - Use the latest post-stabilization run evidence; do not compare against earlier runs if the test code, waits, setup, or selector logic changed afterward.
   - Report the comparison in chat using this table format:

     | Check | automation-js original | auto_tester migration |
     | --- | --- | --- |
     | Command | `<command>` | `<command>` |
     | Result | `<scenario/step pass-fail count>` | `<test pass-fail count>` |
     | Duration | `<duration>` | `<duration>` |
     | Duration improvement | Baseline | `<percent faster/slower than original>` |
     | Scope coverage | `<what original covered>` | `<how mapping preserves it>` |
     | Quality notes | `<legacy stability/selector/wait notes>` | `<selector stability, waits, cleanup, intentional workflow differences>` |

   - Summarize under the table whether scope was preserved against `migration_mapping.md`.
   - Summarize under the table whether quality was preserved or improved, including selector stability, waits, cleanup, and any intentional workflow differences.
9. After the migration satisfies the Definition Of Done, use the `update-migration-coverage-tracker` skill to update the Confluence coverage tracker with real run evidence and current progress totals.
10. After stabilization changes, re-check `steps.md`, `script.md`, and `test.py` together:
   - Make sure the phase docs do not claim assertions that were removed from executable code.
   - If an assertion is intentionally removed as redundant or out of scope, document why behavior coverage is still preserved.
   - Re-run the migration comparison after those changes.

## Definition Of Done

The migration is complete only when all three checks pass:

- **High Quality**: phase files are synchronized, helpers are reused or extracted, Python compiles, lints are clean, and changes are logged.
- **Zero Scope Loss**: every legacy assertion, setup path, edge case, and data-table expectation was checked against the local `migration_mapping.md`; the mapping file itself stays out of the PR.
- **Pre-Stress Legacy Gate Passed**: after 3 successful migrated runs and before any stress test, scope and quality were re-verified against the legacy test and confirmed to be at least equivalent.
- **Proven Stability**: focused run passes, resolved heal requests are deleted, and repeated runs pass with fresh auto-created accounts.
- **Runtime And Coverage Comparison**: original automation-js and migrated auto_tester runs are both executed, then reported with durations, pass/fail counts, scope preservation, and quality preservation.
- **Coverage Tracker Updated**: the Confluence coverage tracker reflects the migrated scope, measured results, stability evidence, and updated remaining counts.

## Translation Rules

- Preserve legacy API setup when the original test used API setup, but verify user-visible behavior through the UI.
- Verify that legacy API setup still persists on the current backend. A legacy endpoint can return `200` but silently drop fields, so confirm the write with an independent read-back (GET) and prefer the endpoint the current product UI actually calls instead of blindly reusing the legacy route.
- Prefer API setup for prerequisites that are not the feature under test.
- Do not replace a legacy UI action with an API call when that UI action is part of the scenario scope, assertion path, or reusable function objective.
- If an API shortcut is considered for speed or stability, first prove the removed UI path is outside the migrated scope and document that decision in `script.md` and `changelog.md`.
- If a legacy API shortcut is not stable in auto_tester, keep the API-created entity and ensure the user-visible state through the UI before asserting downstream behavior.
- Use `data-qa` selectors first, then roles/labels, then stable text. Use raw CSS only for existing stable project selectors such as CRM table actions. If no stable selector exists, document the fallback in `script.md` and suggest the exact `data-qa` that should be added to the product code.
- Replace fixed sleeps with condition waits. Poll only for asynchronous product indexing or eventual consistency, and make the expected condition explicit.
- Keep matter/client terminology entity-agnostic unless the legacy scenario specifically asserts a displayed label.
- Do not preserve a legacy implementation detail when it is only a Selenium workaround; preserve the behavior and assertion instead.

## Migration Patterns Proven By The PoC

- A legacy write endpoint may silently no-op on the current backend: `PUT /v2/settings` returned `200` but dropped `tips`, while the POV reads and writes tips via `POST /platform/v1/payment/settings`. Confirm persistence with an independent GET read-back and use the endpoint the current FE calls.
- Legacy Gherkin tables become explicit expected lists in `test.py`.
- Legacy `scenarioContext` values become `context[...]` keys.
- Legacy `POST /platform/v1/clients` setup maps to an auto_tester helper using `context["auto_account"].api_token`.
- Legacy CRM filter assertions need dynamic waits because CRM indexing can lag API-created clients.
- Legacy Client Card settings status chips map to the Client status tab in `Settings / Client & Contact info`.
- In-use delete protection can be asserted by the status remaining present; a blocking dialog may or may not be displayed depending on current UI behavior.
- Do not duplicate behavior checks across migrated scenarios just because the legacy helper chain allowed it; if one migrated scenario already owns CRM filter coverage, a delete scenario can stay focused on Client Card deletion behavior when that matches the legacy page object source of truth.

## Skill Extraction Checkpoint

Only create or update a reusable migration skill after a real migration passes the DoD. Do not extract rules from failed attempts, unresolved heal requests, or behavior that was not validated by runner output.
