# Changelog: crm_mobile_list

## 2026-06-20 - Initial migration (VCITA2-14251)
- Migrated from `automation-js/features/steps/crm-mobile.feature` (`@mobile_web`,
  scenario "CRM mobile list"). Only the active legacy steps are in scope; the
  commented-out legacy steps (products, open-payments tab, tags filter, scroll-load,
  client-card redirect) are disabled in legacy and excluded.
- Legacy ground-truth run PASSED before building: 1 scenario / 12 steps, 44.16s on
  directory `recurly`, command
  `node index features/steps/crm-mobile.feature integration --headless`.
- Mobile emulation: legacy used Chrome mobile-emulation (`Nexus 5`). First attempt was a
  plain `set_viewport_size(390x844)` — INSUFFICIENT: vcita kept its desktop layout
  (sidebar) mounted and the mobile welcome bottom-sheet never appeared. Fixed by
  replicating Nexus 5 emulation via CDP in `set_mobile_viewport`: device metrics
  (`mobile: true`, 360x640, scale 3) + `setTouchEmulationEnabled` + mobile-UA
  `setUserAgentOverride`. The runner builds the context with `no_viewport=True`, so this
  per-page emulation takes effect. New project pattern (no prior `set_viewport_size`/CDP
  mobile usage). Applied in the test phase (after login), so the captcha-bypass UA on the
  login navigation is unaffected.
- Mobile layout DOM differs from desktop: the mobile CRM does NOT render
  `.table-actions__filter` (it uses `CrmTable-<tab>-filter-button` + a bottom-nav shell),
  so the desktop `crm_*_helpers.wait_for_clients_table` could not be reused for
  navigation/tab-select. `crm_mobile_helpers` is self-contained with mobile-local
  `open_clients_list` / `select_tab` whose readiness signal is the active view's
  `summary-text` counter becoming visible (confirmed via a live DOM probe). The
  counter / empty-state / search-bar / row-name selectors are identical to the legacy
  `newClients.js` page object and the desktop `crm_tabs_helpers`.
- Reused: `account_api.create_client` (seeding, in `_setup`).
- New helper module `crm_mobile_helpers.py`: `set_mobile_viewport` (CDP mobile emulation),
  `open_clients_list`, `select_tab`, `assert_clients_counter` (bounded poll-and-reload),
  `assert_empty_state`, `search_in_tab` (bounded re-search), `close_crm_mobile_welcome_modal`
  (legacy `RolloutBottomSheet-footer-button`), `seed_csv_clients` (loops
  account_api.create_client over the 10 CSV rows).
- Both tab switches (New inquiries -> All) kept, mirroring the legacy comment that the
  switch gives the seeker time to index the new clients.
- Wait audit: all UI waits 5s; counter/search asserts use the existing bounded poll
  helpers (≤ INDEX_RELOAD_ATTEMPTS / SEARCH_ATTEMPTS). No timeouts > 5s, no retry loops > 2
  added by this test.
