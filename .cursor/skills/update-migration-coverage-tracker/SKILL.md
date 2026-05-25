---
name: update-migration-coverage-tracker
description: Update the automation-js to auto_tester Confluence coverage tracker after a legacy automation-js Gherkin feature or scenario is fully migrated, validated, and compared. Use when a migration reaches done, when backfilling migration coverage, or when the user asks to update migration progress totals.
---

# Update Migration Coverage Tracker

## When To Use

Use this skill only after a migration has enough evidence to update shared coverage:

- The legacy automation-js scope is identified.
- The migrated auto_tester scope is implemented and validated.
- Original and migrated runs were executed, with result and duration captured.
- Scope coverage was checked against `migration_mapping.md`.

Do not mark a row `Migrated` from partial implementation, failed focused runs, unresolved heal requests, or guessed runtime data.

## Tracker Location

- Confluence page: `automation-js to auto_tester Migration Coverage Tracker`
- Page ID: `4690444289`
- Cloud ID: `myvcita.atlassian.net`
- Parent page: `auto_tester Project Guide`

Use the Confluence MCP tools when available. Before calling an MCP tool, read its descriptor under the local MCP folder.

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

1. Fetch the current Confluence page in markdown.
2. Add or update one row in the Migration Coverage table for the migrated scope.
   - Prefer one row per legacy feature file when the full file is migrated.
   - If only selected scenarios from a feature file are migrated, make that clear in `Scope covered` and update scenario progress only.
3. Update Summary rows:
   - `Migration progress by feature file`
   - `Migration progress by scenario`
   - `Migrated feature files`
   - `Validated auto_tester scopes`
   - latest migrated scope, Jira, and branch when this migration is the newest one.
4. Preserve the `Scope Counting Rules`, `Update Instructions`, and `Status Definitions` sections.
5. Remove stale `Backfill needed` entries only after replacing them with real run evidence.
6. Publish the complete page body, not a partial section.
7. Fetch the page again and verify the updated rows rendered.

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

## Final Response

After updating Confluence, report:

- Page URL and new version.
- The progress totals after the update.
- The row that was added or changed.
- Any missing data left as `TBD` or `Backfill needed`.
