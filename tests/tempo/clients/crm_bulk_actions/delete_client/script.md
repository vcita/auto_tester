# Script — Delete Client From CRM (Bulk Action)

Playwright-oriented HOW for `test.py`. Helpers live in
`tests/clients/crm_bulk_actions/crm_bulk_helpers.py`.

## API setup
- `account_api.create_client(context, first, last, email)` ×2 → `POST /platform/v1/clients`.
  Names/emails carry a per-test run token (`tok`); the deletion targets the 2nd client.

## UI flow (CRM top-level POV page at `/app/clients`)
- `open_clients_list`.
- `select_client(full_name)` → select `first02_<tok> last02` (rendered checkbox wrapper).
- `bulk_delete()` → `[data-qa="bulk-action-button-more"]` → `[data-qa="item-delete"]` →
  confirm `[data-qa="vc-footer-Delete"]` → acknowledge `[data-qa="vc-footer-OK"]`
  (all top-level POV) → wait the clients table again.

## Assertion
- `verify_remaining_after_delete(tok, [first01_<tok> last01])`:
  the legacy reads the whole table on a fresh 2-client account and asserts only
  `first01 last01` remains. On the shared isolated account this is scoped by
  searching the CRM for the per-test token (so only this test's two clients are
  candidates) and asserting the visible set equals `[first01_<tok> last01]`.
  Reload-and-re-search up to 2 retries to absorb seeker-index lag after delete.

## Selector / wait policy
- `data-qa` first; client names read from `[data-qa="matter-name"]`,
  search via `[data-qa="CrmTable-All-actionBar-searchBar"]`.
- All UI waits ≤5s; no fixed sleeps; post-delete index lag handled with bounded
  reload-and-recheck (≤2 retries).
