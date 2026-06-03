# Script — Create, Edit and Remove CRM Filters

Playwright-oriented HOW for `test.py`. Helpers live in
`tests/clients/crm_filters/crm_filters_helpers.py`.

## API setup
- `create_client(context, {first_name, last_name, email[, tags]})` →
  `POST /platform/v1/clients` (tags passed as top-level key, like legacy).
- `create_product(context, name, price)` →
  `POST /business/payments/v1/products` `{product:{...}, new_api:true}`.
- `assign_product(context, client_id, product_id, price)` →
  `POST /business/payments/v1/product_orders` (creates the open payment).

## UI flow (CRM is the POV Vue page at `/app/clients`)
- Readiness: `wait_for_clients_table` waits for `.table-actions__filter` and no
  visible loaders. All filter actions scope to the active view
  (`.v-window-item--active`).
- Filters menu: click `.table-actions__filter`, then the option `data-qa`:
  - First Name: `item-fields_filter.first_name` → text `[data-qa="VcDropdown-content"] input` → apply `[data-qa="VcDropdown-content"] .VcButton`.
  - Tags: `item-tags_filter` → pick option → apply.
  - Open payments: `item-matter_metadata_flat.payments.open` (toggle, no apply).
- Active chips: `.active-filters .VcChip`; chip name = `.vc-tooltip__activator span span` (first).
- Remove chip: `button.v-chip__close`; clear all: `Clear all` text.
- Counter: `.v-window-item--active [data-qa="summary-text"]`.
- Client names: `[data-qa="matter-name"]`.
- Views: `Recently active` via `[data-qa="crm-view-more-button"]` → `[name="Recently active"]`;
  save fixed-as-new via `.table-actions__save--margin` → modal `crm-save-view-modal` → name → `vc-footer-Save`;
  save custom via `button.table-actions__save` → `.save-action-items__item`.

## Selector / wait policy
- `data-qa` first, then role/text, then CSS.
- No fixed sleeps. UI waits capped at 5s. Active-filter, counter, and
  filtered-client reads use bounded polls (≤5s) with a reload-and-recheck loop
  to absorb seeker indexing lag.
- Active-filter assertions compare the *set* of active filters (order-agnostic)
  to avoid brittleness on newest-first chip ordering while preserving scope.
