# Changelog — Display and Filter by Custom Field

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
