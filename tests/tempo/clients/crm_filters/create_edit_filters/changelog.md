# Changelog — Create, Edit and Remove CRM Filters

## 2026-06-15 — Stabilize Step 11 save-view click (VCITA2-14064)
- Flake (stress 3/5): `Timeout 30000ms exceeded` in Step 11 (`save_custom_view`).
  Root cause: the shared `_click_visible` helper called `locator.click()` with no
  explicit timeout, so a transiently non-actionable Save split-button (a just-dismissed
  save/toast overlay briefly intercepting pointer events in the CRM views toolbar) hung
  on Playwright's default 30s actionability wait, then failed.
- Fix: `_click_visible` now clicks with an explicit `UI_TIMEOUT` (5s) cap and a single
  bounded re-resolve+retry. No fixed sleep; converts a 30s hang into a fast bounded retry
  that clears the transient overlay. No scope/assertion change.
- Second 30s flake (stress 9/10, Step 11 again): untimed `inner_text()` reads on a filter
  chip mid-removal during the post-save `assert_displayed_filters([])` poll hit Playwright's
  default 30s and killed the poll. Fix: the chip/row/counter/column readers now read text via
  a defensive `_safe_text` (explicit 5s cap, returns None on transient detach) so the enclosing
  poll retries until the DOM settles. No scope/assertion change.
  (A first attempt also set a global `page.set_default_timeout(5s)` in `open_clients_list`,
  but that regressed the sibling `custom_field_filtering` `add_column` reload/manage-columns
  flow, which legitimately relies on the longer default while the SPA re-fetches field
  metadata. Reverted — `_safe_text` already caps the reads with explicit timeouts.)

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

## 2026-06-03 — Scope parity + save-view stability
- Restored the legacy counter assertion `1 CLIENTS` on the `Recently active`
  view (feature line 26), which was previously only asserting the filter chip.
- Hardened the save-view flow (`save_fixed_as_new_view`/`save_custom_view`):
  bounded (5s) visibility waits before every click via `_click_visible`, and
  scoped the modal/menu/footer to the visible instance to avoid the default 30s
  actionability timeout on mounted-but-hidden panels. Validated 5/5 clean runs.

### Open items (validated during runs)
- Confirm a fresh auto_account starts with 0 clients so the `4 CLIENTS` counter
  holds. If not, relax the counter assertion.
- Confirm the `Recently active` built-in view shows exactly the expected
  `Last activity time` chip.
- Confirm the open-payment propagates to the `Open payments` CRM index.

## 2026-06-14 — Isolated account + deterministic "Recently active"
- Subcategory now runs in its own isolated (fresh) account, matching the legacy
  fresh-per-scenario account. In the shared clients boundary account the
  accumulated sibling activity inflated the `Recently active` count to
  `4 CLIENTS`; a fresh account is required for the `1 CLIENTS` assertion.
- The `Recently active` view filters on last-activity time, which is driven by a
  real interaction (an appointment), not by an open payment in this environment
  (confirmed by the sibling `recently_active` migration). `create_edit_filters`
  now seeds an appointment for the open-payment client (`first3`) so it is the
  single recently-active client; `first3` keeps its open payment for the later
  Open-payments filter.
- Added `select_view_until_counter` (reload + re-select, bounded to 3 attempts)
  for the index-lag-sensitive `Recently active` counter, and hardened
  `clear_all_filters` with a bounded, retried click (avoids the default 30s
  actionability hang on a re-rendering "Clear all" control). Validated 4/4 clean
  subcategory runs + a full `clients` boundary run.
