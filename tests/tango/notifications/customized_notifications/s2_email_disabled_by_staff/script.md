# Script — Customized Email Notification Disabled By Staff (v3)

`test_s2_email_disabled_by_staff(page, context)`

Shared helpers (nc) + `account_api`. Directory token is the v3 Bearer; owner staff uid via
`account_api.first_staff_uid`.

## Data
- `seq`, `code = f"new_auto_notification{seq}"`, `display = f"Customized Email Notification {seq}"`,
  `description = "This is a test notification template."`, `token`, `staff_uid`.

## Flow
1. `nc.ensure_owner_session(page, context)`.
2. `nc.create_notification_template_v3(... configurable_by_staff=True, content={email:{...}})`
   (no staff_portal, per the legacy scenario-2 table).
3. `nc.goto_settings`; `nc.assert_template_in_settings(code, display, description)`.
4. `nc.set_channel_checkbox(page, code, "email", checked=False)` — UI uncheck + save (reused;
   this UI action is the scenario's behavior, kept as UI not API).
5. `nc.goto_settings` (= "refresh the page"); `nc.assert_channel_values(page, code, {"email":"false"})`.
6. `uid = nc.send_notification_v3(context, token, code, staff_uid, params=[{name:Business Name}])`,
   then `nc.assert_v3_channel_not_dispatched(context, token, uid, "email")`.
   Legacy asserted the SEND *failed* (null uid on a non-2xx) when the only channel was
   staff-disabled. On the CURRENT backend the send returns 201 but does NOT dispatch the
   disabled channel: `email_status` stays null/empty (vs `["in_progress"]` when enabled). We
   assert that behavior-equivalent outcome — the staff-disabled channel is not delivered — which
   is a more direct check than the old HTTP-failure proxy (verified live; see changelog).

## Waits / selectors
- Settings + checkbox waits via reused helpers, ≤5s. The checkbox is toggled with the proven
  JS-level click (set_channel_checkbox) because the Vuetify ripple intercepts a normal click.
- The not-delivered assertion reads the v3 GET channel status once (single read; the disabled
  channel is suppressed synchronously in the send record).
