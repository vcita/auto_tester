# Display and Filter by Custom Field

Migrated from `automation-js/features/steps/crm-filters-create-and-edit.feature`
scenario **Display and filter by custom field** (VCITA2-13790).

## Goal
Verify that custom fields can be shown as CRM table columns and used to filter
the client list.

## Preconditions
- The 4 base clients from the sibling `create_edit_filters` test (reused via the
  shared account; recreated if absent).
- A matter singleline field `client_field` and a client dropdown field
  `dropdown_field` (options option_a/b/c), both created via account API.
- 2 more clients: `first5` (client_field=text_value, dropdown_field=option_a),
  `first6` (client_field=text_value, dropdown_field=option_b).

## Steps
1. Open the clients list (All tab), clear filters.
2. Add the `client_field` column → it appears in the CRM table header.
3. Add the `dropdown_field` column → it appears in the CRM table header.
4. Filter by `client_field` = `text_value` → clients: first5, first6.
5. Filter by `dropdown_field` = `option_b` → clients: first6.
6. Clear all filters → all 6 clients.

## Expected results
- Both custom-field columns appear in the table header.
- The filtered client list matches the expected clients at each step.
