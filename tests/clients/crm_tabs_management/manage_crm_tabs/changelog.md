# Changelog — manage_crm_tabs

## 2026-06-09 — Initial migration (VCITA2-13992)
- Migrated `automation-js/features/steps/crm-tabs-management.feature` (Scenario: "Manage
  CRM table tabs") to `tests/clients/crm_tabs_management`.
- Reused `crm_views_helpers` for navigation, tab clicking (`select_view`), `close_tab`,
  and the views-dropdown read (`_unpinned_view_names`).
- New `crm_tabs_helpers`: `assert_empty_state`, `assert_clients_counter`, `search_in_tab`
  (bounded re-search for CRM seeker indexing lag), `drag_tab` (drag handle onto target
  tab, manual-mouse fallback for vuedraggable), `assert_tab_before` (horizontal x order),
  `assert_tab_in_views_dropdown`, and `create_self_client` (API setup with owner email so
  the row renders "(You as a client)").
- Background livesite leave-details submission replaced by API client creation + an API
  appointment booking (out-of-scope setup). A bare API client never appears in the
  "Recently active" view (no last-activity); the booking registers recent activity, the
  same effect the legacy livesite submission had. Validated by the "(You as a client)"
  label and "Recently active" search assertions.

## Wait audit
- `search_in_tab` retries up to `SEARCH_ATTEMPTS=6` with a `SEARCH_RETRY_WAIT_MS=1500`
  inter-attempt wait. This exceeds the >2-retry guideline but is justified: it targets a
  genuine async readiness signal (CRM seeker indexing lag for the API-created client and
  its booking). The legacy `clientsSearchBar` used 8 retries with 3-7s delays; this is
  tighter. No timeout exceeds the 5s cap; all other waits are condition-based.
