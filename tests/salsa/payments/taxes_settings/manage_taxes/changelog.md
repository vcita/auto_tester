# Manage Taxes - Changelog

## 2026-05-30 - Initial migration
- Migrated automation-js `features/salsa/payments-settings/taxes-settings.feature`
  (single scenario `Create, update & delete taxes`) to a single auto_tester leaf test
  `manage_taxes` under a new `tests/payments/taxes_settings/` subcategory.
- Mapped the legacy `pages/desktop/Frontage/Settings/taxes.js` page object to
  `taxes_helpers.py`, reusing its stable `data-qa` selectors
  (`line-tax-{name}-{rate}`, `tax-name`, `tax-rate`, `tax-delete`, `tax-menu-actions-0`,
  `radio-include` / `radio-exclude`, `action-button-payments_settings-save`).
- Account uses `account_profile: isolated` so the taxes list starts empty, making the
  exact list assertions deterministic (legacy relied on a fresh automatic account).
- Replaced legacy implicit waits with explicit condition waits: row data-qa materialization
  after typing, success-toast wait after save, and a short poll when asserting the list to
  absorb reactive re-render.
- Scope boundary vs existing `tests/payments/settings/set_tax_rates`: that test covers
  create + "apply default tax to items" + persistence; this migration adds the net-new
  edit, delete, multi-tax list verification, and tax-mode (include/exclude) coverage. The
  "apply default tax to items" flow is out of legacy scope and intentionally not duplicated.

## 2026-05-30 - Code review fix
- `add_tax` now targets the new empty row `line-tax-undefined-undefined` (matching the legacy
  page object) instead of the `.last` input, removing a latent race where the second add could
  target the first row before the new row rendered. Both input element handles are resolved up
  front via `_resolve_handle`, which also guards against a `None` handle. Removed the now-unused
  `_type` helper.

## 2026-05-30 - Velocity optimization
- Replaced the save confirmation: the previous `SUCCESS_TOAST` selector never matched, so every
  one of the 4 saves burned the full 8s toast timeout (~32s total wasted). `save_changes` now
  waits for the actual persisting response (`.../payments/v1/tax_bulk` for create/edit/delete,
  `.../v2/settings` for the tax-mode change) via `page.expect_response`, which is both faster
  (~0.3s/save) and a stronger, true server-side save confirmation than the toast.
- `edit_tax` now retries on a detached node: the faster save surfaced a race where the Vue list
  re-renders (swapping row nodes) just after the save response, detaching a freshly resolved
  element handle. The retry re-resolves and re-applies both values, keeping the edit deterministic.
- `manage_taxes` resolves the tax-rows scope once and reuses it for edit/delete/mode instead of
  re-opening the settings page three times (no navigation occurs between steps).
- Result: category runtime ~62s -> ~40s (Manage Taxes phase ~50s -> ~22s), 10/10 stress stable,
  scope and assertions unchanged.

## 2026-05-30 - Code review hardening
- `save_changes` now takes an explicit `endpoint` and each save waits for its own endpoint
  (`tax_bulk` for create/edit/delete, `/v2/settings` for the tax-mode change) so an unrelated
  settings request can no longer satisfy the wait early.
- Extracted named constants (`TAX_BULK_ENDPOINT`, `SETTINGS_ENDPOINT`, `DETACHED_NODE_HINT`,
  `EDIT_RETRIES`, `EDIT_RETRY_PAUSE_SECONDS`) to remove magic strings/numbers and document the
  fragile-but-necessary Playwright detached-node string check.
- Re-validated 10/10 stress stable.
