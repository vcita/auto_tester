# Script — Add/Edit/Hide/Show/Delete Client Portal Action

Single test: `test_manage_actions(page, context)`.

All editor interactions go through `cp_actions_helpers` (nested-iframe topology:
`page -> iframe[title="angularjs"] -> #vue_iframe_layout`). Livesite verification
opens a fresh client context (`?client_jwt=<portal_token>`) and reads the
`#cp_iframe` action buttons, polling past the CP action cache.

1. `open_editor(page, context)` — navigate to `/app/client-portal-editor`.
2. `add_action(page, context, "Contact us", "Leave details 1")`.
3. `assert_cp_displays(page, context, portal_token, "Leave details 1")`.
4. `edit_action(page, "Leave details 1", "Leave details 2")` — no portal re-check (CP cache).
5. `hide_action(page, "Leave details 2")`.
6. `assert_cp_not_displays(page, context, portal_token, "Leave details 2")`.
7. `show_action(page, "Leave details 2")` — no portal re-check (CP cache).
8. `delete_action(page, "Leave details 2")`.
9. `assert_cp_not_displays(page, context, portal_token, "Leave details 2")`.
