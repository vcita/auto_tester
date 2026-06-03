# Changelog — Create, Edit and Remove CRM Filters

## 2026-06-03 — Initial migration (VCITA2-13790)
- Migrated scenario `User creates, edits and removes filters` from
  `automation-js/features/steps/crm-filters-create-and-edit.feature`.
- API setup: 4 base clients (2 tagged `tag4`), a product, and a product order
  assigned to `first3` to create an open payment.
- UI: First Name / Tags / Open payments filter apply, edit, remove, clear;
  fixed-as-new view and custom view save. Reused the proven CRM read/filter
  patterns from `tests/clients/custom_status/status_helpers`.
- Assertions per step: active-filter chip set, filtered client list (bounded
  reload-and-recheck for seeker lag), and the client counter.
- Stores the 4 base client names in `context["crm_base_clients"]` for the
  sibling `custom_field_filtering` test (shared account).

### Open items (validated during runs)
- Confirm a fresh auto_account starts with 0 clients so the `4 CLIENTS` counter
  holds. If not, relax the counter assertion.
- Confirm the `Recently active` built-in view shows exactly the expected
  `Last activity time` chip.
- Confirm the open-payment propagates to the `Open payments` CRM index.
