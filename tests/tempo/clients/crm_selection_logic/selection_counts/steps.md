# Checkbox Selection Counts

Migrated from `automation-js/features/steps/crm-selection-logic.feature` scenario
**Check checkbox selection logic** (VCITA2-13862).

## Goal
Verify the CRM client-list selection summary line counts correctly when selecting a
single client, the current page, and all pages — both on the full list and after
searching to a filtered subset.

## Preconditions (created via account API)
- 12 clients on a fresh isolated account: `first01 last01` … `first11 last11`
  (11 clients) plus `other other` (1 client).

## Steps
1. Open the clients list.
2. Set rows per page to 10.
3. Sort the table by client name (ascending, so `first01 last01` is on page 1).
4. Select a single client (the first visible row) → summary is `1 SELECTED OF 12 CLIENTS`.
5. Select the current page → summary is `10 SELECTED OF 12 CLIENTS`.
6. Select all pages → summary is `12 SELECTED OF 12 CLIENTS`.
7. Search `first` (filters to the 11 `firstNN` clients) and select a single client
   → summary is `1 SELECTED OF 11 CLIENTS`.
8. Select the current page → summary is `10 SELECTED OF 11 CLIENTS`.
9. Select all pages → summary is `11 SELECTED OF 11 CLIENTS`.

Note: the legacy selects `first01 last01` specifically, but the assertion is the
selection **count** (identity-agnostic); selecting the first visible row is equivalent
and avoids any dependency on sort order / pagination.

## Expected results
- The summary line shows the exact `N SELECTED OF M CLIENTS` value after each action.
