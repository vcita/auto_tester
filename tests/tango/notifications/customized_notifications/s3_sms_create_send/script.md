# Script — Create And Send Customized SMS Notification (v3)

`test_s3_sms_create_send(page, context)`

Shared helpers (nc) + `account_api`. Directory token is the v3 Bearer; owner staff uid via
`account_api.first_staff_uid`.

## Data
- `seq`, `code = f"new_auto_notification{seq}"`, `display = f"Customized SMS Notification {seq}"`,
  `description = "This is a test notification template."`, `token`, `staff_uid`.

## Flow
1. `nc.ensure_owner_session(page, context)`.
2. `nc.create_notification_template_v3(... content={sms:{message_body:[{en:"SMS Message Body with ${name}"}]}})`.
3. `nc.goto_settings`; `nc.assert_template_in_settings(code, display, description)`.
4. `nc.set_channel_checkbox(page, code, "sms", checked=True)` — UI enable the SMS channel + save
   (reused; the enable is the scenario's behavior, kept as UI).
5. `uid = nc.send_notification_v3(context, token, code, staff_uid, params=[{name:Business Name}])`.
   Assert `uid` truthy (legacy "passed").
6. `nc.assert_v3_channel_status_contains(context, token, uid, "sms", "in_progress")` — bounded
   poll of the v3 GET sms_status.

## Waits / selectors
- Settings + checkbox waits via reused helpers, ≤5s. SMS checkbox toggled with the proven
  JS-level click (set_channel_checkbox). v3 sms status is a bounded eventual-consistency poll (≤5s).
