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
