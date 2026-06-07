# Changelog — Checkbox Selection Counts

## 2026-06-07 — Initial migration (VCITA2-13862)
- Migrated `automation-js/features/steps/crm-selection-logic.feature` scenario
  `Check checkbox selection logic`.
- Created isolated subcategory `clients/crm_selection_logic` (fresh account so the
  `N SELECTED OF M CLIENTS` counts are deterministic).
- Added `crm_selection_helpers.py` reusing generic CRM primitives from
  `crm_bulk_actions/crm_bulk_helpers.py` (open list, select client, select all pages,
  search) and adding `set_rows_per_page`, `sort_by_client_name`, `select_current_page`,
  `assert_summary_text`.
- Summary line read via inner_text (rendered) + case-insensitive compare to mirror the
  legacy Selenium getText(); count assertion polls ≤5s for the re-render.
- Selectors: all `data-qa` except the rows-per-page footer control
  (`.VcTableFooter--itemsPerPage` / `.option-text`) — documented fallback (no data-qa).

## 2026-06-07 — Restore named-client selection + exact summary match
- Single-client selection now targets the named client `first01 last01`
  (`select_client_by_name`) instead of "the first row", so sort + rows-per-page stay
  an oracle (the named client must land on the current page after the sort), matching
  legacy `selects client "first01 last01"`.
- `assert_summary_text` now compares with exact string equality (was
  case-insensitive), matching legacy `summaryText.should.be.eq(text)`.
- script.md timing wording corrected: the 0.2s sleep is the poll interval inside the
  bounded ≤5s re-render poll, not a blind fixed sleep.
- `select_client_by_name` keeps each element wait at the 5s UI cap but wraps the named
  row in a bounded retry (≤3 attempts, re-gating on `wait_for_clients_table` between
  attempts) to absorb the search-index reload settle that the lenient first-row
  selection used to mask — mirrors the async-list retry pattern in crm_bulk_helpers.
