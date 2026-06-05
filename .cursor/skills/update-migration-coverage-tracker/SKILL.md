---
name: update-migration-coverage-tracker
description: Update the automation-js to auto_tester Confluence coverage tracker after a legacy automation-js Gherkin feature or scenario is migrated, stabilized, validated, and compared. Use when a migration reaches done, when a migrated test is stabilized, when backfilling migration coverage, or when the user asks to update migration progress totals.
---

# Update Migration Coverage Tracker

After a migration is validated, record it by running one committed tool. The tool
upserts the per-feature row in the Google Sheet and refreshes the Confluence
dashboard in place — never hand-edit either artifact.

## When To Use

Use after a migration has enough evidence to update shared coverage:

- The legacy automation-js scope is identified.
- The migrated auto_tester scope is implemented and validated.
- Original and migrated runs were executed, with result and duration captured.
- Scope coverage was checked against `migration_mapping.md`.

Also use after **stabilizing** an already-migrated test when the row should reflect new evidence:

- The stabilized scope maps to an existing migrated legacy feature or scenario.
- The stabilization run produced real focused or `stress_test` output.
- Status, stability evidence, migrated runtime, or duration improvement changed.

Do **not** mark a row `Migrated` from partial implementation, failed focused runs, unresolved heal requests, or guessed runtime data.

## How It Works

The tracker has two synced artifacts, both owned by `tools/migration_tracker`:

| Artifact | Holds | Updated by the tool |
|----------|-------|---------------------|
| **Google Sheet** (source of truth) | The full per-feature coverage table — one row per migrated scope (scope, runtime comparison, stability, Jira, PR). | Row upserted, matched by feature file. |
| **Confluence dashboard** (page `4690444289`, cloud `myvcita.atlassian.net`, parent "auto_tester Project Guide") | A rich page: Summary metrics, two colored progress bars, Scope Counting Rules, Update Instructions, Status Definitions. The old big coverage table is replaced by a link to the Sheet. | Bars + Summary metric rows refreshed **in place**; other sections untouched. |

Why a tool and not hand-edited HTML:

- The single-page coverage table grew past the Confluence MCP argument-size limit and could no longer be published — so it moved to the Sheet.
- The page is published as **ADF** (`atlas_doc_format`). The storage/HTML importer silently strips table-cell background colors and status lozenges, so ADF is the only format that keeps the colored bars.
- Publishing replaces the whole page body. **Never** do a manual or "probe" write to the live page (it overwrites everything). Always go through the tool, which fetches the current page, edits it in place, and republishes the full doc.

One-time setup (service-account key, Sheet id, Confluence email + API token) is in `tools/migration_tracker/README.md`. If the env vars are unset, stop and follow the README.

## Required Data

Collect before running:

- Legacy feature path, e.g. `features/steps/client-custom-status.feature`.
- Migrated auto_tester path, e.g. `tests/clients/custom_status`.
- Status: `Migrated`, `Needs stabilization`, `Blocked`, `In progress`, or `Proposed`.
- Scope covered — summarized from the original scenario actions and assertions.
- Original result and duration (automation-js run).
- Migrated result and duration (auto_tester run). The tool auto-normalizes the duration to the `Xm SSs` format used by the original column.
- Duration improvement vs the original.
- Stability evidence — only real focused or `stress_test` output.
- Jira link and PR link, or `TBD` if unavailable.

For a stabilization-only update, keep the existing original-run data and change only the migrated result, duration, status, stability evidence, Jira, or PR.

## Counting Rules

Compute these with a structured parser or a small script — never from memory:

- **Total feature files**: all `*.feature` files under `automation-js/features`.
- **Total scenarios**: lines starting with `Scenario:` or `Scenario Outline:`.
- **Migrated feature files**: distinct feature paths whose *full* scenario set is covered by migrated rows. Do not count a file as migrated when only some of its scenarios are migrated.
- **Migrated scenarios**: original scenarios covered by migrated rows.
- **Remaining** = total − migrated, for each.

Count script:

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

Duration improvement:

```text
improvement = (original_seconds - migrated_seconds) / original_seconds * 100
```

Format as `N.N% faster` (positive) or `N.N% slower` (negative).

## Update Workflow

1. Confirm the `tools/migration_tracker/README.md` env vars are set.
2. Compute the current totals with the Counting Rules above.
3. Upsert the row and refresh Confluence in one call (matched by `--feature`; updates if present, appends otherwise). Pass the Summary metrics you computed; any Summary row you omit is left unchanged:

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

   - For a partial migration, make the migrated scenario(s) clear in `--scope` and do not increment `--ff-migrated` until every scenario in the file is migrated.
   - For a stabilization-only update, pass the same `--feature` to update the existing row (no duplicate).
   - `--ff-*`/`--sc-*` drive the bars and the two "candidate progress" Summary rows (the tool derives the "N left" counts). `--tracked-*`/`--validated-scopes` set their Summary rows; `--latest-*`/`--jira-key` set the "Latest" rows.
4. To preview without publishing, use the `confluence` subcommand with `--emit <file>` (writes the ADF doc).
5. Verify: open the printed Sheet URL (row present/updated) and the Confluence page version, and confirm the bars/percentages and Summary rows match what you passed.

## Reference

### Sheet columns (one row per migrated scope)

| Feature file | auto_tester path | Status | Scope covered | Original result | Migrated result | Duration improvement | Stability | Jira | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `features/...` | `tests/...` | Migrated | concise scope | `scenario/step count`, `duration` | `pass count`, `duration` | `N.N% faster` | focused/stress evidence | Jira link | PR link or TBD |

For a partial feature-file migration, keep the feature path and name the migrated scenario(s) in `Scope covered`; do not count the file as migrated until every scenario is.

### PR link format

- Merged or open PR: `PR #<number>` → `https://github.com/vcita/auto_tester/pull/<number>` (pass via `--pr-label` / `--pr-url`).
- No PR yet, branch pushed: use the branch link and `(PR TBD)`; replace with the PR number once opened (`gh pr view <branch>` or `gh pr list --head <branch>`).

### Duration improvement integrity

Only record an improvement when the migrated scope still covers every original assertion, setup path, and in-scope UI action. If runtime dropped because coverage, selectors, or in-scope actions were reduced, do not present it as an improvement — note the scope/quality change instead.

## After Updating

Report:

- The Sheet URL and the new Confluence page version.
- The progress totals after the update.
- The row that was added or changed.
- Any missing data left as `TBD`.
