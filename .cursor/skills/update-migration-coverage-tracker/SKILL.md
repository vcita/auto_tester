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

- Confluence page: `automation-js to auto_tester Migration Coverage Tracker`
- Page ID: `4690444289`
- Cloud ID: `myvcita.atlassian.net`
- Parent page: `auto_tester Project Guide`

Use the Confluence MCP tools when available. Before calling an MCP tool, read its descriptor under the local MCP folder.

## Preserve Table Layout (Critical)

The Migration Coverage table is rendered with the Confluence **full-width** table layout. This layout lives in the ADF/HTML table element as `data-layout="full-width"` (ADF attr `"layout": "full-width"`). It is NOT expressible in markdown, so updating the page with `contentFormat: markdown` silently resets the table back to default width.

To keep the layout across updates:

- Always fetch and publish with `contentFormat: html` (not markdown).
- Keep the Migration Coverage table tag as `<table data-layout="full-width">`. The three narrow tables (Summary, Scope Counting Rules, Status Definitions) stay plain `<table>`.
- After publishing, re-fetch in `adf` and confirm the Migration Coverage table still shows `"layout": "full-width"` (and that the narrow tables stay `"default"`).

Note: per-column widths (the ADF `colwidth` cell attribute, set by dragging column borders in the editor) are stripped by the API HTML importer and cannot be set or preserved through these tools — only the `full-width` table layout can.

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

1. Fetch the current Confluence page with `contentFormat: html` (not markdown — markdown drops the full-width table layout; see "Preserve Table Layout").
2. Add or update one row in the Migration Coverage table for the migrated scope.
   - Prefer one row per legacy feature file when the full file is migrated.
   - If only selected scenarios from a feature file are migrated, make that clear in `Scope covered` and update scenario progress only.
   - If stabilizing an existing migrated scope, update the existing row instead of adding a duplicate row.
   - Edit the HTML in place: keep `<table data-layout="full-width">` for the Migration Coverage table and insert/modify the row's `<tr>...</tr>` without touching other cells.
3. Update Summary rows:
   - `Migration progress by feature file`
   - `Migration progress by scenario`
   - `Migrated feature files`
   - `Validated auto_tester scopes`
   - latest migrated scope, Jira, and branch when this migration is the newest one.
4. Preserve the `Scope Counting Rules`, `Update Instructions`, and `Status Definitions` sections.
5. Remove stale `Backfill needed` entries only after replacing them with real run evidence.
6. Publish the complete page body with `contentFormat: html`, not a partial section, keeping `data-layout="full-width"` on the Migration Coverage table.
7. Fetch the page again in `adf` and verify both the updated rows AND that the Migration Coverage table still shows `"layout": "full-width"`.

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
