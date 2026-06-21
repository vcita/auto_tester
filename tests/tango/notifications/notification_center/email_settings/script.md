# Script — Email Channel In Notification Center Settings

`test_email_settings(page, context)` — helpers in `notifications_helpers.py`.

## API preconditions (core_internal_app token)
- `ci_token = core_internal_app_token(context)` — admin `POST /oauth/service/token` with the
  integration core_internal_app service creds (env/default).
- `create_notification_template(context, ci_token, code=auto_nc_email_settings<seq>,`
  `type=payments, channel={pane:true,push:true}, deep_link="app/reports", text={...})`.

## Flow (settings page locators identical to nc_settings)
0. `ensure_owner_session(page, context)` — clean session + re-login as the account owner so
   this test is independent of prior subcategory tests.
1. Settings page. `assert_template_in_settings(code, display_name="Automation NC Email`
   `Settings <seq>", description="Notification description")`.
   `assert_channel_values(code, {push:"true", pane:"true", email:"hidden"})` — email checkbox
   element absent because the template has no email channel yet.
2. `update_notification_template(ci_token, code, {channel:{email:true}})`. Reload settings.
   `assert_channel_values(code, {push:"true", pane:"true", email:"true"})`.

## Waits
UI waits `timeout=5000`. "Refresh" = re-navigate to the settings page. No fixed sleeps.
