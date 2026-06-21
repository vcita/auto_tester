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
  set `In review`. After the PR merges, run the tracker again to flip the row to `Merged`,
  refreshing **both** the Sheet and Confluence (`--refresh-confluence` with the current
  ff/sc totals re-passed so the bars don't reset).
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

> **The two progress bars are NOT "left unchanged when omitted" — they are redrawn from the totals you pass.** The "omitted ⇒ unchanged" rule applies only to the Summary metric *rows*. The bars are driven by `--ff-migrated/--ff-total/--sc-migrated/--sc-total`, which default to `0`; if you pass `--refresh-confluence` **without** those totals, `_refresh_bars` redraws both bars at `0 / 0` and wipes the progress. So whenever you use `--refresh-confluence`, always pass the current ff/sc totals.
>
> **When a test PR merges, update BOTH the Sheet and Confluence.** Flip the row to `Merged` **and** pass `--refresh-confluence` on the same upsert. The `In review → Merged` flip does not change the progress counts, but Confluence must still be refreshed so the page reflects the merge and the "Latest migrated scope / Latest Jira / Latest branch" rows stay current. Because `--refresh-confluence` **redraws the bars from the totals you pass**, you MUST re-pass the current ff/sc totals (`--ff-migrated/--ff-total/--sc-migrated/--sc-total`) and the `--tracked-*`/`--validated-scopes`/`--latest-branch` values on the merge upsert — otherwise `_refresh_bars` resets the bars to `0 / 0` and wipes the progress.

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

### Reading the current row before re-upserting

The tool has no `show`/`get` command, so before a one-field change (e.g. flipping `In review → Merged`) read the existing row so you can re-pass every column verbatim. Fetch with `valueRenderOption=FORMULA` so the Jira/PR `HYPERLINK` URLs come back (needed for `--jira-url`/`--pr-url`):

```bash
python3 - <<'PY'
from tools.migration_tracker import config
from tools.migration_tracker.google_sheets import SheetsClient

client = SheetsClient(config.GSA_KEY_PATH, config.require("SHEET_ID", config.SHEET_ID))
resp = client._session.get(
    f"https://sheets.googleapis.com/v4/spreadsheets/{config.SHEET_ID}/values/{config.SHEET_TAB}",
    params={"valueRenderOption": "FORMULA"},
)
for row in resp.json().get("values", []):
    path = row[1] if len(row) > 1 else ""
    if "<your/auto_tester/path>" in path:  # filter to the row(s) you're editing
        print(row)
PY
```

Copy `Scope covered`, `Original result`, `Migrated result`, `Duration improvement`, and the Jira/PR URLs out of the printed row and re-pass them on the upsert so nothing is blanked.

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
2. Compute the current totals with the Counting Rules above. **The `--ff-total`/`--sc-total` numbers in the example below are illustrative and go stale** — read the live Confluence page's current Summary first (or recompute via the Counting Rules) and pass the **live** totals (as of this writing the live page is `136` feature files / `362` scenarios, not the older `113`/`279`). Passing stale totals with `--refresh-confluence` rewrites the progress bars to the wrong denominator.
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
     --ff-migrated <n> --ff-total 136 --sc-migrated <n> --sc-total 362 \   # use the LIVE totals (step 2), not these literals
     --tracked-ff <n> --tracked-sc <n> --validated-scopes <n>
   ```

   - For a partial migration, make the migrated scenario(s) clear in `--scope` and do not increment `--ff-migrated` until every scenario in the file is migrated.
   - For a stabilization-only update, pass the same `--feature` to update the existing row (no duplicate). **Re-pass every column** (`--scope`, `--original`, `--migrated`, `--improvement`, `--stability`, …) — the upsert rewrites the whole row, so omitted columns are blanked, even when you only meant to add a PR link.
   - `--ff-*`/`--sc-*` drive the bars and the two "candidate progress" Summary rows (the tool derives the "N left" counts). `--tracked-*`/`--validated-scopes` set their Summary rows; `--latest-*`/`--jira-key` set the "Latest" rows.
4. To preview without publishing, use the `confluence` subcommand with `--emit <file>` (writes the ADF doc).
5. Verify: open the printed Sheet URL (row present/updated) and the Confluence page version, and confirm the bars/percentages and Summary rows match what you passed.
6. **After the PR merges**, run the same upsert again for that `--feature` with `--status Merged` (re-pass every column, since the upsert rewrites the whole row — read the current row first if needed, see "Reading the current row before re-upserting"). This is the only time a row should read `Merged`. Update **both artifacts**: pass `--refresh-confluence` so the Confluence page reflects the merge and its "Latest" rows stay current. Because `In review → Merged` doesn't change progress counts but `--refresh-confluence` redraws the bars from the args, you MUST re-pass the current ff/sc totals (`--ff-migrated/--ff-total/--sc-migrated/--sc-total`) plus `--tracked-*`/`--validated-scopes`/`--latest-branch`; the bars stay put while the page is refreshed.

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

## Sync the Jira ticket (status + retrospective comment)

Every tracker status change must be mirrored on the row's `VCITA2` Jira ticket (via the
`manage-jira-issues` skill). Transition the ticket to the matching status:

- `In progress` / `Needs stabilization` → **In Progress** (transition id `11`)
- `In review` → **In Review** (id `31`)
- `Merged` → **Done** (id `51`)
- `Blocked` → **Blocked** (id `41`)

**When the row moves to `In review`, also post a migration-retrospective comment** on the ticket
(`addCommentToJiraIssue`, `contentFormat: markdown`) covering *what went well and what was hard*:
scenario→subtest mapping + scope/zero-loss note, helper reuse, and especially **stabilization
challenges with their root cause and fix** (flaky selectors, cold-load/skeleton races, async
propagation, overlay/wizard interference, backend/UI behaviour changes, mechanism/scope
deviations), plus the final stress result and how many runs it took. Keep it tight and use **flat
bullets** — nested/ordered lists do not survive the markdown→ADF conversion (they render empty).

## After Updating

Report:

- The Sheet URL and the new Confluence page version.
- The progress totals after the update.
- The row that was added or changed.
- The Jira transition applied (and, at `In review`, that the retrospective comment was posted).
- Any missing data left as `TBD`.
