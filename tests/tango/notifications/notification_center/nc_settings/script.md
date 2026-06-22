# Script — Notification Center Settings

`test_nc_settings(page, context)` — helpers in `notifications_helpers.py`.

## API preconditions (directory token)
- `dir_token = directory_token(context)` — env/default `ff333ad7960d32e873d48d5de772f826`
  (the integration directory 970 autotester provisions on).
- `create_notification_template(context, dir_token, code=auto_nc_settings<seq>, type=payments,`
  `channel={pane:true,push:true}, deep_link="app/clients", show_in_settings=false, text={...})`.

## Settings page (POV) — see notifications_helpers
Settings opened by navigating the toolbar to the Notification Center settings, then the page
renders inside iframe `#vue_iframe_layout`, container `.notification`. Row by code
`[data-qa="<code>"]`; display name `.notification__description--name`; description
`.notification__description--sub`; channel checkbox `[data-qa="checkbox-<type>-<code>"]`
(`aria-checked` = "true"/"false"; element ABSENT = "hidden"); save
`[data-qa='VcPageHeader-saveButton']`.

## Flow
0. `ensure_owner_session(page, context)` — the runner shares one browser across the
   subcategory's tests and notification_flow ends impersonated as "Staff Admin"; clear the
   session and re-login as the account owner so this test runs as the owner (legacy
   per-scenario `user logged in to automatic account`).
1. `assert_template_not_in_settings(code)` — settings page; the row `[data-qa="<code>"]` is
   absent (show_in_settings=false). Legacy: `findNotificationInSettings(...).length == 0`.
2. `update_notification_template(dir_token, code, {show_in_settings:true})`. Reload settings
   (the legacy "refresh the page" — re-navigate to settings, not page.reload).
   `assert_template_in_settings(code, display_name="Automation NC Settings <seq>",`
   `description="Notification description")`. `assert_channel_values(code, {push:"true", pane:"true"})`.
3. `update_notification_template(dir_token, code, {channel:{push:false}})`. Reload settings.
   `assert_channel_values(code, {push:"hidden", pane:"true"})`.
4. `open_notification_settings(page)` — open the pane, click settings button
   `[data-qa="notifications-settings"]`; assert the settings page loaded (notification names
   visible). Legacy `notificationSettingsLoaded`.
5. `send_notification(dir_token, code, staff_uid)`. `goto_dashboard` (the live badge push is
   reliable on the dashboard, stale on the heavy settings iframe). `assert_badge_counter("1")`.
   `open_pane` (marks notifications seen server-side); `assert_notification_displayed(title=
   "Check this out!", body="Hi! A new message is available", timestamp="Just now",
   status="unread")`. `close_pane`.
6. `goto_settings`; `set_channel_checkbox(code, "pane", checked=false)` (uncheck pane, save).
   `send_notification(dir_token, code, staff_uid)`. `goto_dashboard`; `assert_no_badge_counter`
   (pane suppressed; opening the pane in step 5 already cleared the prior unseen count).

## Waits
UI waits `timeout=5000`. Badge counter uses the bounded re-check. "Refresh" = re-navigate to
the settings page (real navigation, not page.reload). No fixed sleeps.
