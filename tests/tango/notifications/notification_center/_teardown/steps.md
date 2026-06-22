# Teardown — Notification Center

Best-effort cleanup of API-created artifacts (the whole isolated account is also deleted by
the runner on a passing run, so this only bounds leftovers):

1. Delete each notification template created by the tests (by code name, via its creator token).
2. Delete the app created by the notification_flow test (admin), if any.

Failures are logged, not fatal (mirrors the legacy best-effort `delete_notification_metadata`
/ `delete_app`, which the legacy run itself tolerates a 401 on).
