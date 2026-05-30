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
