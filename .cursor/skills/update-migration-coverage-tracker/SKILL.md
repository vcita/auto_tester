---
name: update-migration-coverage-tracker
description: Update the automation-js to auto_tester Confluence coverage tracker after a legacy automation-js Gherkin feature or scenario is migrated, stabilized, validated, and compared. Use when a migration reaches done, when a migrated test is stabilized, when backfilling migration coverage, or when the user asks to update migration progress totals.
---

# Update Migration Coverage Tracker

## When To Use

Use this skill only after a migration has enough evidence to update shared coverage:

- The legacy automation-js scope is identified.
- The migrated auto_tester scope is implemented and validated.
- Original and migrated runs were executed, with result and duration captured.
- Scope coverage was checked against `migration_mapping.md`.

Also use this skill after stabilizing an already migrated test when the tracker row should reflect new evidence:

- The stabilized auto_tester scope maps to an existing migrated legacy feature or scenario.
- The stabilization run produced real focused or `stress_test` output.
- Status, stability evidence, migrated runtime, or duration improvement changed.

Do not mark a row `Migrated` from partial implementation, failed focused runs, unresolved heal requests, or guessed runtime data.

## Tracker Location

The tracker has two synced artifacts:

- **Google Sheet** — holds only the full per-feature coverage table (scope, runtime comparison, stability, Jira, PR). One row per migrated scope.
- **Confluence dashboard** — a rich page kept as-is: Summary metrics, the two colored progress bars, Scope Counting Rules, Update Instructions, and Status Definitions. The old big coverage table is replaced by a link to the Google Sheet.
  - Page ID: `4690444289`
  - Cloud ID: `myvcita.atlassian.net`
  - Parent page: `auto_tester Project Guide`

Both are updated by one committed tool, `tools/migration_tracker` (see its `README.md` for one-time service-account + env setup). Do not hand-edit the sheet or the Confluence page — run the tool so the row, bars, and Summary metrics stay consistent.

## Why The Tool (Not Hand-Edited HTML)

The old single-page full-width table grew past the Confluence MCP argument-size limit and could no longer be published. Only that table moved to the Google Sheet; the rest of the page is preserved. The tool edits the page **in place** (refreshing the bars and the Summary metric rows, leaving every other section untouched) and publishes as **ADF** — the storage/HTML importer silently strips table-cell background colors and status lozenges, so ADF is the only format that keeps the colored bars.

## Required Data

Collect these values before editing the page:

- Legacy feature path, for example `features/steps/client-custom-status.feature`.
- Migrated auto_tester path, for example `tests/clients/custom_status`.
- Migrated status: `Migrated`, `Needs stabilization`, `Blocked`, `In progress`, or `Proposed`.
- Scope covered, summarized from the original scenario actions and assertions.
- Original result and duration from the automation-js run.
- Migrated result and duration from the auto_tester run.
- Duration improvement, calculated against the original duration.
- Stability evidence, using only real focused or `stress_test` output.
- Jira link and PR link, or `TBD` if unavailable.

For stabilization-only updates, keep existing original run data unless new legacy evidence was collected. Update only the changed migrated result, duration, status, stability evidence, Jira, or PR fields.

## Counting Rules

Keep these summary metrics current:

- Total feature files: count all `*.feature` files under `automation-js/features`.
- Total scenarios: count lines starting with `Scenario:` or `Scenario Outline:` under `automation-js/features`.
- Migrated feature files: count distinct feature paths whose full scenario set is covered by migrated rows. Do not count a feature file as migrated when only some of its scenarios were migrated.
- Migrated scenarios: count original scenarios covered by migrated rows.
- Remaining feature files: total feature files minus migrated feature files.
- Remaining scenarios: total scenarios minus migrated scenarios.

Use a structured parser or a small script for counts. Do not update totals by memory.

## Update Workflow

Run the committed tool from the repo root; it upserts the sheet row and re-publishes the Confluence dashboard in one call.

1. Confirm setup once: `tools/migration_tracker/README.md` env vars are set (service-account key, sheet id, Confluence email + API token). If unset, stop and follow the README.
2. Compute the current totals using the Counting Rules below (a small parser, never from memory): migrated feature files, total feature files, migrated scenarios, total scenarios.
3. Upsert the row and refresh Confluence in one call (matched by `--feature`; updates if present, appends otherwise). Pass the Summary metrics you computed in step 2; any Summary row you omit is left unchanged:

   ```bash
   python -m tools.migration_tracker.update_tracker upsert \
     --feature <legacy/feature/path.feature> \
     --path <tests/auto_tester/path> \
     --status Migrated --scope "<concise scope>" \
     --original "<scenarios/steps, duration>" \
     --migrated "<pass count, duration>" --improvement "<N.N% faster>" \
     --stability "<focused/stress evidence>" \
     --jira-key <VCITA2-XXXX> --jira-url <jira url> \
     --pr-label "PR #<n>" --pr-url <pr url> \
     --latest-branch "<branch> — PR #<n>" \
     --refresh-confluence \
     --ff-migrated <n> --ff-total 113 --sc-migrated <n> --sc-total 279 \
     --tracked-ff <n> --tracked-sc <n> --validated-scopes <n>
   ```

   - Prefer one row per legacy feature file when the full file is migrated. For a partial migration, make the migrated scenario(s) clear in `--scope` and do not increment `--ff-migrated` until every scenario in that file is migrated.
   - For a stabilization-only update, pass the same `--feature` to update the existing row in place (do not create a duplicate).
   - `--ff-*`/`--sc-*` drive the bars and the two "candidate progress" Summary rows (the tool derives the "N left" counts). `--tracked-*`/`--validated-scopes` set the corresponding Summary rows; `--latest-*`/`--jira-key` set the "Latest" rows.
4. To preview the edited page without publishing, use the `confluence` subcommand with `--emit <file>` (writes the ADF doc).
5. Verify: open the printed sheet URL (row present/updated) and the Confluence page version, and confirm the bars/percentages and Summary rows match what you passed.

## Commands

Count legacy totals from the `automation-js` repository:

```bash
python3 - <<'PY'
from pathlib import Path

features = sorted(Path("features").rglob("*.feature"))
scenarios = 0
for path in features:
    text = path.read_text(errors="ignore")
    scenarios += sum(
        1
        for line in text.splitlines()
        if line.lstrip().startswith(("Scenario:", "Scenario Outline:"))
    )

print(f"FEATURE_FILES={len(features)}")
print(f"SCENARIOS={scenarios}")
PY
```

Calculate duration improvement:

```text
improvement = (original_seconds - migrated_seconds) / original_seconds * 100
```

Format as `N.N% faster` when positive, or `N.N% slower` when negative.

## Row Format

Use this Migration Coverage table structure:

| Feature file | auto_tester path | Status | Scope covered | Original result | Migrated result | Duration improvement | Stability | Jira | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `features/...` | `tests/...` | Migrated | concise scope summary | `scenario/step count`, `duration` | `test pass count`, `duration` | `N.N% faster` | focused/stress evidence | Jira link | PR link or TBD |

For partial feature-file migrations, keep the same feature path but write the migrated scenario name(s) in `Scope covered`; do not increment `Migrated feature files` until every scenario in that feature file is migrated.

## PR Link Format

Write the `PR` cell consistently with the existing rows:

- Merged or open PR: `[PR #<number>](https://github.com/vcita/auto_tester/pull/<number>)`
- No PR yet, branch pushed: `[branch <branch-name>](https://github.com/vcita/auto_tester/tree/<branch-name>) (PR TBD)`

Replace the branch placeholder with the `PR #<number>` link as soon as the PR is opened. Find the number with `gh pr view <branch-or-number>` or `gh pr list --head <branch>`. Use the same `PR #<number>` template for the `Latest` Summary field when this is the newest migration.

## Reduce Waits And Duration (Without Scope Or Quality Loss)

When recording `Duration improvement`, confirm the speedup did not come from reduced scope or weakened quality:

- Only record a duration improvement when the migrated scope still covers every original assertion, setup path, and in-scope UI action.
- If runtime dropped because coverage, selectors, or in-scope UI actions were reduced, do not present it as an improvement; note the scope/quality change instead.
- Keep `Scope covered` and `Quality notes` consistent with the recorded duration improvement.

## Final Response

After updating Confluence, report:

- Page URL and new version.
- The progress totals after the update.
- The row that was added or changed.
- Any missing data left as `TBD` or `Backfill needed`.
