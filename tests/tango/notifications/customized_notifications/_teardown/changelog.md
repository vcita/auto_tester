# Changelog — _teardown (customized_notifications)

## 2026-06-19 — Created (VCITA2-14248 migration)
- Best-effort v3 DELETE of every created template (uid) via `delete_notification_template_v3`
  (legacy `Deleting created notification metadata`). Isolated account is also runner-deleted.
