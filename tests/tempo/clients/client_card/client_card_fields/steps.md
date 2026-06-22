# Client and contact custom card fields

Migrated from `automation-js/features/steps/client-card.feature` — scenario
"client card fields" (VCITA2-13855).

## Scope
Add custom fields through Client Card Settings, prove they are usable as CRM
filters, and rename them.

## Steps
1. Add a **client** field named `client_field` of type **Single line text** (Client Card Settings).
2. Create a client `first last` with `client_field = blublublu` via API.
3. Filter the CRM client list by `client_field = blublublu` → the list shows exactly **first last**.
4. Rename the client field `client_field` → `client_field_1` (verify the new name renders).
5. Add a **contact** field named `contact_field` of type **Single line text**.
6. Create a client `first1 last1` with `contact_field = test field` via API.
7. Filter the CRM client list by `contact_field = test field` → the list shows exactly **first1 last1**.
8. Rename the contact field `contact_field` → `contact_field_1` (verify the new name renders).

## Notes
- The legacy scenario comments out the re-search after each rename due to bug
  **SUPPORT-6006**, so only the rename action is verified here (no post-rename
  filter assertion), preserving the original scope exactly.
- Filters are cleared before each field filter so each assertion is independent.
