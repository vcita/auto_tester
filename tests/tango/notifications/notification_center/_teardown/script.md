# Teardown Script — Notification Center

`teardown_notification_center(page, context)`

1. For each `(code, token)` recorded in `context["nc_templates"]`: best-effort
   `delete_notification_template(context, token, code)` (apigw DELETE). Log + swallow errors.
2. For each app code in `context["nc_apps"]`: best-effort `delete_app(context, code)`
   (admin DELETE `/platform/v1/apps/<code>`). Log + swallow errors.
