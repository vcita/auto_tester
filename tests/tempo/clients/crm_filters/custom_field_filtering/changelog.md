# Changelog — Display and Filter by Custom Field

## 2026-06-15 — Align `add_column` to legacy 90s poll (VCITA2-14064)
- Ran the original automation-js scenario (`crm-filters-create-and-edit.feature:84`):
  it PASSES when the integration CRM seeker is healthy (56s) and FAILS identically when
  it is lagging (`TimeoutError: loader itemSkeleton still found on page NewClients`).
  So `client_field never appeared in manage-columns` is the same backend-index lag, not a
  test-logic divergence — the matter-field-as-column path itself is faithful and correct.
- Learned from legacy: its column lookup is `getItemFromListByText` → `findInElements`
  wrapped in a `this.wait(operation_timeout=90s)`, i.e. it opens the manage-columns dialog
  once and POLLS the OPEN list for the field; it does not reload on a 30s budget.
- Fix: `add_column` now polls the open dialog (re-querying) for `COLUMN_POLL_SECONDS` before
  falling back to a metadata-refetching reload, with the field-index budget raised 30s→90s
  to match the legacy `operation_timeout`. Untimed reload/clicks in the column path are now
  capped (no Playwright default 30s hang). No scope/assertion change.

## 2026-06-03 — Initial migration (VCITA2-13790)
- Migrated scenario `Display and filter by custom field` from
  `automation-js/features/steps/crm-filters-create-and-edit.feature`.
- API setup: matter singleline field `client_field`, client dropdown field
  `dropdown_field` (option_a/b/c), and 2 clients with custom-field values.
  Reuses the 4 base clients from the sibling test (shared account) and recreates
  them if the context key is absent.
- UI: add both custom fields as CRM columns and verify the headers; filter by
  the singleline field and the dropdown field; clear all.

### Open items (validated during runs)
- Confirm `/platform/v1/clients` persists custom-field values by label; else set
  values via the fields-values API.
- Confirm `/platform/v1/fields` accepts the dropdown type + possible_values;
  else create the dropdown field via the client-card settings UI.
