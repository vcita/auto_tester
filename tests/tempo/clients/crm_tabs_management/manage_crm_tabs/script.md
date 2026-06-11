# Manage CRM Table Tabs — Script

Reuses `crm_views_helpers` for navigation/tab/view actions and `crm_tabs_helpers` for the
tab-specific reads/actions. All selectors mirror the legacy `newClients.js` `data-qa`.

## Step 1 — New inquiries empty
- `select_view(page, "New inquiries")` (clicks the pinned tab, waits for the table).
- `assert_empty_state(page)` -> active view `[data-qa="VcEmptyState"]`.
- `assert_clients_counter(page, "0 CLIENTS")` -> active view `[data-qa="summary-text"]`.

## Step 2 — Recently active search
- `select_view(page, "Recently active")` (picks it from the `crm-view-more-button`
  overflow dropdown via `[name="Recently active"]`, becomes a pinned tab).
- `search_in_tab(page, "Recently active", "form_first", [self_client_label])` ->
  search bar `[data-qa="CrmTable-<tab>-actionBar-searchBar"]`, rows
  `[data-qa="CrmTable-<tab>-item-matter_name"]`. Bounded re-search for seeker indexing lag.
- `assert_clients_counter(page, "1 CLIENTS")`.

## Step 3 — Drag reorder
- `drag_tab(page, "New inquiries", "All")` -> drag handle `[data-qa="VcTabs-drag-<from>"]`
  onto tab `[data-qa="VcTabs-tab-All"]` (drag_to with manual-mouse fallback for
  vuedraggable).
- `assert_tab_before(page, "New inquiries", "All")` -> compares the two tabs' horizontal x.

## Step 4 — Close tab -> dropdown
- `close_tab(page, "New inquiries")` (reused; clicks tab, close icon, confirms unpinned).
- `assert_tab_in_views_dropdown(page, "New inquiries")` -> overflow dropdown includes it.

## Waits
- All waits are condition-based (`wait_for`, `expect.to_have_text`, bounded polls ≤ 5s).
- The search re-issue loop is bounded (`SEARCH_ATTEMPTS`) for CRM seeker indexing lag;
  no fixed sleeps.
