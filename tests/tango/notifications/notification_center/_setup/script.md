# Setup Script — Notification Center

`setup_notification_center(page, context)`

1. Read `username`/`password` from context (isolated account). Fail if missing.
2. `fn_login(page, context, username, password)` — UI login (reuses `tests/_functions/login`).
3. Store `context["nc"] = {"seq": <epoch>}` for tests to derive unique code names.

No notification template is created here — each test creates its own via the
`notifications_helpers` API with the token kind its scenario uses.
