# Changelog — delete_client

## 2026-06-05 — Initial migration (VCITA2-13798)
- Migrated from `automation-js/features/steps/crm-bulk-actions.feature` scenario
  "Delete client from CRM".
- Created `steps.md`, `script.md`, `test.py`.
- Flow: create 2 clients via account API → open `/app/clients` → select `first02 last02`
  → bulk "Delete" (confirm + OK) → search by per-test token → assert only
  `first01 last01` remains.
- Delete confirm/OK dialogs are top-level POV (`vc-footer-Delete` / `vc-footer-OK`),
  reusing the proven bulk-delete pattern. Verified live on integration before coding.
- Legacy reads the whole table on a fresh account; scoped here via CRM search on the
  per-test token to stay exact on the shared isolated account. Post-delete index lag
  handled with bounded reload-and-recheck. Waits ≤5s, no fixed sleeps.

## 2026-06-05 — Delete verification hardened (validation fix)
- CRM search ignores a bare numeric token but matches the alpha-prefixed name, so a
  single shared-token search returned no rows. Verification now uses two
  token-unique queries (`first01_{token}` / `first02_{token}`): the remaining client
  must still be found and the deleted client's search must be empty.
- A default 30s Playwright timeout could occur while reading the list during the
  post-delete re-render: `visible_client_names` now uses `all_inner_texts()` (one
  snapshot) instead of `nth(i).inner_text()`, and `search_clients` uses an atomic
  `fill(timeout=5s)` instead of click + `press_sequentially` (avoids post-delete
  toast click interception).
- Delete index lag gets more reloads than other checks (`DELETE_ATTEMPTS = 5`).
