# Teardown Script — Customized Notifications

`teardown_customized_notifications(page, context)`

1. For each `(uid, token)` in `context["nc_templates_v3"]`, call
   `notifications_helpers.delete_notification_template_v3(context, token, uid)` (best-effort;
   tolerates errors, like the legacy delete).
