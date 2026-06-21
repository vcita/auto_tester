# Teardown — Customized Notifications

Best-effort cleanup of the API-created v3 templates (mirrors the legacy best-effort
`Deleting created notification metadata`). The whole isolated account is also deleted by the
runner on a passing run, so this only bounds leftovers.

1. Delete every v3 notification template created during the subcategory (by uid, directory token).
