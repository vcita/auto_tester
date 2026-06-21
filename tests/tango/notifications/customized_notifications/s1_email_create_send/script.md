# Script — Create And Send Customized Email Notification (v3)

`test_s1_email_create_send(page, context)`

Shared helpers from `tests.tango.notifications.notification_center.notifications_helpers` (nc)
and `tests.account_api`. The directory token is the v3 API Bearer (legacy
`get_authorization_token("directory")`); the staff uid is the account owner
(`account_api.first_staff_uid`, legacy `get_staffs(pivot)[0].id`).

## Data
- `seq = context["nc"]["seq"]`; `code = f"new_auto_notification{seq}"`.
- `display = f"Customized Email Notification {seq}"`; `updated_display = f"Customized Email Notification Updated Title {seq}"`.
- `description = "This is a test notification template."`
- `token = nc.directory_token(context)`; `staff_uid = account_api.first_staff_uid(context)`.

## Flow
1. `nc.ensure_owner_session(page, context)` — clean owner session (subcategory reuses one context).
2. `template = nc.create_notification_template_v3(context, token, code_name=code,
   category="payments", configurable_by_staff=True, title=[{locale:en,value:display}],
   description=[...], content={email:{subject, main_title, main_text, primary_cta_button:{text}},
   staff_portal:{...}})`. Keep `template_uid = template["uid"]` (the TEMPLATE uid, used for the
   update + teardown DELETE). The helper also records it for v3 teardown.
3. `nc.goto_settings(page, context)` then `nc.assert_template_in_settings(page, code,
   display_name=display, description=description)` — the v3 template shows in NC settings by
   `[data-qa="<code>"]` (same settings DOM the existing helper drives; data-qa first).
4. `notif_uid = nc.send_notification_v3(context, token, code, staff_uid, params=[{key:name,value:Business Name}])`.
   Assert `notif_uid` is truthy (legacy "passed"). NOTE: this is the staff-NOTIFICATION uid,
   distinct from `template_uid`.
5. `nc.assert_v3_notification_created(context, token, notif_uid)` — GET by the staff-notification
   uid returns data (legacy "new notification created").
6. `nc.update_notification_template_v3(context, token, template_uid, {title:[{en:updated_display}],
   content:{email:{primary_cta_button:{text:[{en:"Primary CTA Button update name"}]}}}})` — the
   UPDATE targets the TEMPLATE uid (a PUT to the staff-notification uid 404s).
7. `nc.goto_settings(page, context)` (= legacy "refresh the page", real re-navigation, NOT
   page.reload). `nc.assert_template_in_settings(page, code, display_name=updated_display,
   description=description)`.
8. `nc.goto_dashboard(page, context)` then `nc.assert_badge_counter(page, "1")` — bounded
   eventual-consistency poll on the toolbar badge (reused helper; dashboard has the live push).
9. `nc.assert_v3_channel_status_contains(context, token, notif_uid, "email", "processed")` —
   bounded poll of the v3 GET email_status (staff-notification uid).

## Waits / selectors
- All UI waits via reused helpers, capped at UI_TIMEOUT (5s). Badge + v3 status are bounded
  eventual-consistency polls (≤5s), no action retried.
- Settings rows use `data-qa="<code>"` + `.notification__description--name/--sub` (reused).
