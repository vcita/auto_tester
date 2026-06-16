# Script — Display and Filter by Custom Field

Playwright-oriented HOW for `test.py`. Helpers in
`tests/clients/crm_filters/crm_filters_helpers.py`.

## API setup
- `create_field(context, object_type, label, field_type[, possible_values])` →
  `POST /platform/v1/fields`. Matter `client_field` (singleline) and client
  `dropdown_field` (dropdown with possible_values).
- `create_client(context, {..., client_field, dropdown_field})` — custom-field
  values passed as top-level keys on the client payload (legacy behavior).

## UI flow
- Columns: `[data-qa="CrmTable-All-manage-columns-button"]` → match the option
  by label in `[data-qa="manage-columns-draggable-list-items--in-item"]` → check
  its `input` → `[data-qa="vc-footer-Done"]`. Headers read from
  `.VcDataTable--header` (uppercased, substring match).
- Filters: `item-custom_fields_filter.client_field` (text) and
  `item-custom_fields_filter.dropdown_field` (check option via
  `.vc-base-list-item[display_value="option_b"] input`) → apply.

## Selector / wait policy
- `data-qa` first; no fixed sleeps; UI waits capped at 5s; filtered-client and
  column-present reads use bounded polls (≤5s) to absorb indexing lag.

## Note
If `/platform/v1/clients` does not persist custom-field values by label, the
setup will fall back to setting field values via the fields-values API (resolved
during validation runs).
