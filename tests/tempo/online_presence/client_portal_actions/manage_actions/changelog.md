# Changelog — Add/Edit/Hide/Show/Delete Client Portal Action

## 2026-06-11 — Initial migration (VCITA2-14060)
- Migrated from automation-js `features/tempo/client-portal-actions.feature`.
- Editor interactions via `cp_actions_helpers` using the nested-iframe topology
  `page -> iframe[title="angularjs"] -> #vue_iframe_layout`. Selectors sourced from the
  legacy page object `pages/desktop/Frontage/clientPortalSettings.js`.
- Livesite verification opens a fresh client context and reads `#cp_iframe`
  `.layout.quick-action` labels (legacy `ClientPortalDashboard.getActionListFromCP`).

### Stability notes
- The editor works on the autotester default directory (970) — no directory/whitelabel
  dependency. Two flakes were fixed:
  1. **Edit portal actions click**: triggers an Angular -> Vue iframe reload; a single
     click can land before the handler attaches or before the inner canvas renders.
     `_enter_edit_mode` now polls/re-clicks within NAV_TIMEOUT until the Add-action
     control appears.
  2. **CP livesite cold load**: `_read_cp_actions` did a hard `.quick-actions`
     `wait_for` that, on a slow cold load, raised `TimeoutError` and escaped the
     `assert_cp_*` retry loop (one slow load = instant failure). It now returns `None`
     on a not-ready livesite so the caller re-opens a fresh context and retries within
     CP_SETTLE (60s).
