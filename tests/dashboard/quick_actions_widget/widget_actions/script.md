# Script — Quick Actions Default And Open

## Flow
1. `open_dashboard(page)` — navigate to `/app/dashboard`, wait for `.quick-actions-widget` visible.
2. `assert_actions(page, DEFAULT_ACTIONS)` — read `data-name` off each `.quick-action-item`
   (strip `item-`), assert the six defaults are present (poll up to 5s for lazy render).
3. `click_action(page, "client")` — click `.quick-action-item[data-name="item-client"]`.
4. `assert_new_client_modal(page)` — the Angular new-client dialog
   (`md-dialog.new-client-dialog-component`) is visible inside `iframe[title="angularjs"]`.

## Selector notes
- The widget renders on the **top-level POV page** (frame `''`), verified live:
  6 `.quick-action-item`, 1 `.quick-actions-widget`, 1 `[data-qa='edit-button']`.
- The new-client modal is Angular, so it lives in the angular iframe — switch via
  `frame_locator('iframe[title="angularjs"]')`.
- No fixed sleeps: visibility/`expect` waits only.
