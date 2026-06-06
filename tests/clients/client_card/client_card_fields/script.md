# Script: Client and contact custom card fields

Playwright/Python implementation notes for `test.py`.

## Setup (API + UI)
- Account: isolated (fresh per run), logged in by the subcategory `_setup`.
- Custom fields are created through the **Client Card Settings** UI
  (`/app/settings/client_card`), which lives inside the Angular `iframe[title="angularjs"]`
  → Vue `#vue_iframe_layout` frame. The platform `/fields` API rejects client/contact
  object types, so the UI is the only path (same as the crm_filters dropdown field).
- Clients are seeded via `POST /platform/v1/clients` with the custom-field slug as a
  top-level key (`client_field` / `contact_field`), matching the legacy "creates new
  client via API" table payload.

## Helpers (`client_card_helpers.py`)
- `add_card_field(page, card_type, label, field_type_label)` — clicks
  "Add client field" / "Add contact field", picks the type, fills the name, confirms.
- `edit_card_field(page, origin, updated)` — opens the matching field row, fills the new
  name, Saves, and waits for the renamed row to render (rename success check; the legacy
  re-search is disabled by SUPPORT-6006).
- `add_field_filter(page, field_name, value)` — clears filters, opens the CRM filter menu,
  clicks the option whose `data-qa` ends with `custom_fields_filter.<field_name>` (matches
  both client/matter and contact namespaces), fills the text value, applies, and waits for
  the table. Reopens/reloads until the just-created field appears in the filter metadata.
- CRM seeding/assertions reuse `tests/clients/crm_filters` helpers
  (`create_client`, `open_clients_list`, `assert_filtered_clients`, `clear_all_filters`).

## Assertions
- After each filter, `assert_filtered_clients` polls (with reload) until the visible client
  names equal exactly the expected single client.
- Each rename is verified by the renamed field row becoming visible in the settings list.

## Timing
- No fixed sleeps. UI waits are bounded (5s). The custom-field → filter-metadata
  propagation uses a bounded reopen/reload loop (30s budget), the same backend-index
  pattern used in crm_filters.
