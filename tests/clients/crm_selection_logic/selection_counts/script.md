# Script — Checkbox Selection Counts

Playwright-oriented HOW for `test.py`. Helpers live in
`tests/clients/crm_selection_logic/crm_selection_helpers.py` (generic CRM primitives
re-used from `crm_bulk_actions/crm_bulk_helpers.py`).

## API setup
- `account_api.create_client(context, first, last, email)` ×12 → `POST /platform/v1/clients`.
  Names are the legacy `firstNN lastNN` (×11) + `other other`; emails carry a per-run
  token only (uniqueness across stress iterations). Display names stay token-free so the
  `first` search matches exactly the 11 `firstNN` clients and the counts stay exact.

## UI flow (CRM top-level POV page at `/app/clients`)
- `open_clients_list`.
- `set_rows_per_page("10")` → `.VcTableFooter--itemsPerPage` → option `.option-text` == "10".
- `sort_by_client_name()` → `[data-qa="CrmTable-All-header-matter_name"]` (ascending → first01 on page 1).
- `select_client_by_name("first01 last01")` → the `[data-qa="CrmTable-All"] tbody tr`
  row matching that name (keeps sort+pagination an oracle: the named client must land
  on the current page) → assert `1 SELECTED OF 12 CLIENTS`.
- `select_current_page()` → `[data-qa="checkbox-dropdown-icon"]` → `[data-qa="item-current"]`
  → assert `10 SELECTED OF 12 CLIENTS`.
- `select_all_pages()` → dropdown → `[data-qa="item-all"]` → assert `12 SELECTED OF 12 CLIENTS`.
- `search_clients("first")` → `[data-qa="CrmTable-All-actionBar-searchBar"]` → wait the
  settled unselected summary `11 CLIENTS` → `select_client_by_name("first01 last01")` →
  assert `1 SELECTED OF 11 CLIENTS`.
- `select_current_page()` → assert `10 SELECTED OF 11 CLIENTS`.
- `select_all_pages()` → assert `11 SELECTED OF 11 CLIENTS`.

## Assertion
- `assert_summary_text(expected)` reads `[data-qa="summary-text"]` via inner_text
  (rendered, respects text-transform like the legacy Selenium getText) and compares with
  exact string equality after whitespace-normalizing (mirrors legacy
  `summaryText.should.be.eq(text)`); polls ≤5s for the re-render.

## Selector / wait policy
- `data-qa` first; rows-per-page is the only CSS-class selector (no data-qa exists on
  the footer items-per-page control — documented fallback; suggest adding
  `data-qa="items-per-page"`).
- All element waits are bounded at 5s; the only sleep is the 0.2s poll *interval*
  inside `assert_summary_text`'s bounded ≤5s re-render poll (poll cadence, not a blind
  pre-assertion sleep); table readiness via skeleton-gone wait.
