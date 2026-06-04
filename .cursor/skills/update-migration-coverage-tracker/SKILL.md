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

## Publishing: MCP Size Limit + REST Fallback (Critical)

This page is large (~48 KB of HTML, ~130 KB as an ADF payload) and keeps growing one
row per migration. The MCP `updateConfluencePage` tool **cannot accept a body this large**:
the call fails to parse almost immediately (error like `Expected ',' or '}' after property
value in JSON at position 75`) regardless of body content, because the oversized argument
is truncated before the tool runs. `getConfluencePage` still works (its large response is
written to a file), so use the MCP only for *reading*.

**Hard rules:**

- **Never** do a small "probe"/test write to the live page to check whether MCP works.
  `updateConfluencePage` replaces the whole body, so a tiny test body **overwrites and
  destroys the page**. (This happened once and forced a full restore.)
- Publish updates via the **Confluence REST API v2 PUT**, sending the modified **ADF**
  (`atlas_doc_format`) built programmatically. This avoids inlining the body into a tool call.

**REST publish workflow (reliable, no large inline emission):**

1. Fetch current ADF for reading (MCP `getConfluencePage` with `contentFormat: adf`, or
   `curl .../wiki/api/v2/pages/<id>?body-format=atlas_doc_format`). Note the current
   `version.number`.
2. Parse the ADF (`json.loads(page["body"])`) and modify it **structurally** in Python:
   - Tables in document order: `0` = Summary, `1` = feature-file progress bar,
     `2` = scenario progress bar, `3` = Migration Coverage (this one carries
     `attrs.layout = "full-width"` — preserved automatically since you edit in place),
     `4` = Scope Counting Rules, `5` = Status Definitions.
   - Summary cells: match each row by its first-cell text, replace the second cell's
     `content` paragraphs.
   - Progress-bar label paragraphs (top-level, start with `Candidate ... migrated:`):
     rebuild as `[strong(label), " ", code("N / M"), " (", strong("P%"), ")"]`.
   - Progress bars are 48-cell single-row tables; each cell is a `tableCell` with
     `attrs.background` of `#ff5630` (filled) or `#dfe1e6` (empty). Flip the next empty
     cell to filled when the rounded percentage crosses a cell boundary
     (`filled = round(48 * migrated / total)`).
   - Append the new coverage row to `tables[3]["content"]` (it is a `tableRow` of
     `tableCell`s; cell text uses `text` nodes with `marks` `{"type":"code"}`,
     `{"type":"strong"}`, or `{"type":"link","attrs":{"href":...}}`). ADF text is plain
     unicode — use literal `&`, `→`, `'` (no HTML entities).
3. Write the PUT payload to a file (avoids shell-escaping a 130 KB body):
   `{"id","status":"current","title","body":{"representation":"atlas_doc_format","value":<adf-as-json-string>},"version":{"number":<current+1>,"message":...}}`.
4. PUT it:
   ```bash
   curl -X PUT -u "<email>:<token>" -H "Content-Type: application/json" \
     "https://myvcita.atlassian.net/wiki/api/v2/pages/4690444289" -d @payload.json
   ```
5. Re-fetch in `adf` and verify the new row, the summary/bar updates, and that
   `tables[3].attrs.layout` is still `"full-width"`.

**Auth:** REST uses HTTP Basic with an Atlassian **API token** (`<email>:<token>`), which is
**separate** from the MCP's OAuth — the MCP working does NOT mean a REST token is valid.
Verify the token first with `curl -s -o /dev/null -w "%{http_code}" -u "<email>:<token>"
https://myvcita.atlassian.net/rest/api/3/myself` (expect `200`). If it returns `401`/`403`,
ask the user for a fresh token (id.atlassian.net → Security → API tokens) before touching
the page — do not fall back to a destructive MCP write.

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

1. Fetch the current Confluence page in `adf` (MCP `getConfluencePage` `contentFormat: adf`, or REST `?body-format=atlas_doc_format`) and parse the ADF. Do NOT plan to publish via MCP — see "Publishing: MCP Size Limit + REST Fallback" (the page is too large for an MCP write).
2. Add or update one row in the Migration Coverage table for the migrated scope.
   - Prefer one row per legacy feature file when the full file is migrated.
   - If only selected scenarios from a feature file are migrated, make that clear in `Scope covered` and update scenario progress only.
   - If stabilizing an existing migrated scope, update the existing row instead of adding a duplicate row.
   - Edit the ADF in place: append/modify the `tableRow` in `tables[3]` (the `full-width` Migration Coverage table) without touching other cells.
3. Update Summary rows:
   - `Migration progress by feature file`
   - `Migration progress by scenario`
   - `Migrated feature files`
   - `Validated auto_tester scopes`
   - latest migrated scope, Jira, and branch when this migration is the newest one.
4. Preserve the `Scope Counting Rules`, `Update Instructions`, and `Status Definitions` sections.
5. Remove stale `Backfill needed` entries only after replacing them with real run evidence.
6. Publish the modified ADF via the REST API v2 PUT (payload from a file), per "Publishing: MCP Size Limit + REST Fallback". Verify the API token first; never fall back to an MCP write.
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
