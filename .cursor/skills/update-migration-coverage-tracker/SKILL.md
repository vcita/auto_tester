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

Do **not** advance a row to `In review` or `Merged` from partial implementation, failed focused runs, unresolved heal requests, or guessed runtime data.

## Status Lifecycle

The `Status` column must reflect where the migration actually is — never jump
straight to a "done" status. A PR is only done once it is **merged**, so a
validated-but-open PR is `In review`, not merged.

| Status | When to set it |
|--------|----------------|
| `Proposed` | Candidate identified (Jira/branch may exist); implementation not started. |
| `In progress` | Phase docs / `test.py` being written; stability gate not yet passed. |
| `Needs stabilization` | Implemented and runnable, but focused/stress runs are not yet green. |
| `In review` | Stability gate passed and the PR is **open but not merged**. This is the status at migration closeout. |
| `Merged` | The PR has been **merged to `master`** — the only true "done". |
| `Blocked` | Work cannot proceed (external dependency, product bug, missing selector); note the blocker in `Scope covered`. |

Rules:

- **Never set `Merged` before the PR is actually merged.** At closeout (PR opened),
  set `In review`. After the PR merges, run the tracker again to flip the row to `Merged`.
- `In review` and `Merged` both require the full stability gate to have passed; do
  not set them from partial work, failed runs, or guessed data.
- The legacy `Migrated` value is retired — classify rows as `In review` (PR open) or
  `Merged` (PR merged) instead. When you touch an old `Migrated` row, re-pass the
  correct lifecycle status based on whether its PR is merged.

## How It Works

The tracker has two synced artifacts, both owned by `tools/migration_tracker`:

| Artifact | Holds | Updated by the tool |
|----------|-------|---------------------|
| **Google Sheet** (source of truth) | The full per-feature coverage table — one row per migrated scope (scope, runtime comparison, stability, Jira, PR). | Row upserted, matched by feature file. **The upsert rewrites the whole row from the args you pass — any column you omit is written blank.** |
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
- Status: one of the values in the Status Lifecycle below (`Proposed`, `In progress`, `Needs stabilization`, `In review`, `Merged`, or `Blocked`). Use `In review` at PR-open closeout and `Merged` only after the PR is merged.
- Scope covered — summarized from the original scenario actions and assertions.
- Original result and duration (automation-js run).
- Migrated result and duration (auto_tester run). The tool auto-normalizes the duration to the `Xm SSs` format used by the original column.
- Duration improvement vs the original.
- Stability evidence — only real focused or `stress_test` output.
- Jira link and PR link, or `TBD` if unavailable.

> **Always pass the complete row data on every upsert — even for a one-field change** (e.g. adding the PR link later). The Sheet upsert rewrites the whole row from the args provided, so any field you omit (`--scope`, `--original`, `--migrated`, `--improvement`, `--stability`, …) is blanked. This is the opposite of the Confluence Summary rows, where an omitted metric is left unchanged. For a stabilization-only update, re-pass the existing original-run data alongside the changed migrated result, duration, status, stability evidence, Jira, or PR.

## Counting Rules

Compute these with a structured parser or a small script — never from memory:

- **Total feature files**: all `*.feature` files under `automation-js/features`.
- **Total scenarios**: lines starting with `Scenario:` or `Scenario Outline:`.
- A row counts toward migration progress once its status is `In review` or `Merged` (stability gate passed, at least a PR open). Rows still `Proposed`, `In progress`, `Needs stabilization`, or `Blocked` do not count.
- **Migrated feature files**: distinct feature paths whose *full* scenario set is covered by `In review`/`Merged` rows. Do not count a file as migrated when only some of its scenarios are migrated.
- **Migrated scenarios**: original scenarios covered by `In review`/`Merged` rows.
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
     --status "In review" --scope "<concise scope>" \
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
   - For a stabilization-only update, pass the same `--feature` to update the existing row (no duplicate). **Re-pass every column** (`--scope`, `--original`, `--migrated`, `--improvement`, `--stability`, …) — the upsert rewrites the whole row, so omitted columns are blanked, even when you only meant to add a PR link.
   - `--ff-*`/`--sc-*` drive the bars and the two "candidate progress" Summary rows (the tool derives the "N left" counts). `--tracked-*`/`--validated-scopes` set their Summary rows; `--latest-*`/`--jira-key` set the "Latest" rows.
4. To preview without publishing, use the `confluence` subcommand with `--emit <file>` (writes the ADF doc).
5. Verify: open the printed Sheet URL (row present/updated) and the Confluence page version, and confirm the bars/percentages and Summary rows match what you passed.
6. **After the PR merges**, run the same upsert again for that `--feature` with `--status Merged` (re-pass every column, since the upsert rewrites the whole row). This is the only time a row should read `Merged`.

## Reference

### Sheet columns (one row per migrated scope)

| Feature file | auto_tester path | Status | Scope covered | Original result | Migrated result | Duration improvement | Stability | Jira | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `features/...` | `tests/...` | In review / Merged | concise scope | `scenario/step count`, `duration` | `pass count`, `duration` | `N.N% faster` | focused/stress evidence | Jira link | PR link or TBD |

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
