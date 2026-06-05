# Migration Coverage Tracker

Keeps the **automation-js → auto_tester migration coverage** in sync from any
teammate's migration run:

- The **Google Sheet** holds only the full per-feature coverage table (scope,
  runtime comparison, stability, Jira, PR). Each migration upserts one row.
- The **Confluence page** stays a rich dashboard — Summary metrics, the two
  colored progress bars, Scope Counting Rules, Update Instructions, and Status
  Definitions — with the old big coverage table replaced by a link to the sheet.
  The tool edits the page **in place**, refreshing only the bars and the Summary
  metric rows and leaving every other section untouched. It publishes as ADF, so
  the colored bars survive (the storage/HTML importer strips cell colors).

```
migrate flow ──► update_tracker upsert ──► 1 row upserted in Google Sheet
                                       └─► Confluence bars + Summary refreshed in place
```

## One-time setup (per teammate)

The tool authenticates to Google with a **service account** (no browser consent),
so it works headlessly for everyone who has the shared key file.

### 1. Create the service account + key (once, by an admin)

1. Google Cloud Console → pick/create a project.
2. **APIs & Services → Library** → enable **Google Sheets API** and **Google Drive API**.
3. **IAM & Admin → Service Accounts → Create service account** (e.g.
   `migration-tracker`). No project roles are required.
4. Open the service account → **Keys → Add key → Create new key → JSON** → download.
5. Note the service-account email (e.g. `migration-tracker@<project>.iam.gserviceaccount.com`).
6. Store the JSON key in the team password manager so teammates can fetch it.

### 2. Create + share the Google Sheet (once, by an admin)

1. Create a blank Google Sheet titled
   `automation-js → auto_tester Migration Coverage`.
2. **Share** it with the service-account email as **Editor**.
3. (Recommended) also share with anyone in the org as **Viewer** so the Confluence
   link opens for everyone.
4. Copy the spreadsheet id from its URL
   (`https://docs.google.com/spreadsheets/d/<THIS_ID>/edit`).

> A service account cannot create files in a normal Drive, so the sheet must be
> created by a human and shared with the SA. The tool only reads/writes cells.

### 3. Create a Confluence API token (once, per teammate)

1. <https://id.atlassian.com/manage-profile/security/api-tokens> → **Create API token**.
2. Note your Atlassian account email + the token.

### 4. Configure env (per teammate)

Put the JSON key somewhere private and set these in `~/dev/.env` (preferred, shared
across repos) or the repo `.env`:

```bash
MIGRATION_TRACKER_GSA_KEY=/Users/<you>/dev/.gsa-migration-tracker.json
MIGRATION_TRACKER_SHEET_ID=<spreadsheet id from step 2>
CONFLUENCE_EMAIL=<your atlassian email>
CONFLUENCE_API_TOKEN=<your atlassian api token>
# optional overrides:
# MIGRATION_TRACKER_SHEET_TAB=Coverage
# CONFLUENCE_PAGE_ID=4690444289
# CONFLUENCE_BASE_URL=https://myvcita.atlassian.net/wiki
```

Never commit the key file or tokens.

Install deps once: `pip install -r requirements.txt`.

## Usage

### One-time seed of an empty sheet

```bash
python -m tools.migration_tracker.update_tracker init --rows /path/to/rows.json
```

`rows.json` is a list whose first item is the header and the rest are 12-field
rows: `[feature, path, status, scope, original, migrated, improvement, stability,
jira_label, jira_url, pr_label, pr_url]`. This writes all rows, applies formatting
(frozen header, wrap, column widths, banding, autofilter), and shares the sheet.

### Per-migration update (the recurring call)

```bash
python -m tools.migration_tracker.update_tracker upsert \
  --feature features/tempo/calendar-settings.feature \
  --path tests/scheduling/calendar_settings \
  --status Migrated --scope "..." \
  --original "2 scenarios / 14 steps, 74.0s" \
  --migrated "3/3, ~43s" --improvement "~42% faster" \
  --stability "stress 10/10 on 2026-06-04" \
  --jira-key VCITA2-13796 --jira-url https://myvcita.atlassian.net/browse/VCITA2-13796 \
  --pr-label "PR #50" --pr-url https://github.com/vcita/auto_tester/pull/50 \
  --latest-branch "VCITA2-13796_migrate_calendar_settings — PR #50" \
  --refresh-confluence \
  --ff-migrated 18 --ff-total 113 --sc-migrated 36 --sc-total 279 \
  --tracked-ff 21 --tracked-sc 42 --validated-scopes 21
```

Matches the row by `--feature` (column A): updates it if present, appends otherwise,
then refreshes the Confluence bars + Summary rows in place.

### Refresh only Confluence (e.g. dry-run the doc)

```bash
python -m tools.migration_tracker.update_tracker confluence \
  --latest-path tests/scheduling/calendar_settings \
  --jira-key VCITA2-13796 --pr-label "PR #50" \
  --latest-branch "VCITA2-13796_migrate_calendar_settings — PR #50" \
  --ff-migrated 18 --ff-total 113 --sc-migrated 36 --sc-total 279 \
  --tracked-ff 21 --tracked-sc 42 --validated-scopes 21 \
  --emit /tmp/tracker_doc.json   # omit --emit to publish
```

## Notes on the numbers

The Confluence numbers (`--ff-*`, `--sc-*`, `--tracked-*`, `--validated-scopes`)
are passed in because deciding what counts as a migrated candidate (partial
scenarios, multi-feature rows, excluded `@unstable`/`@wip` scopes) needs the
judgment described in the `update-migration-coverage-tracker` skill. The sheet
stores the per-row detail; these drive the bars and the Summary metric rows. Any
Summary row whose value you don't pass is left unchanged.

`--base-file <adf.json>` is a one-time escape hatch: edit a saved ADF doc instead
of the live page (used to restore the page from version history). Normal runs omit
it and edit the live page.
