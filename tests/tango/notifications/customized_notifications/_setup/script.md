# Setup Script — Customized Notifications

`setup_customized_notifications(page, context)`

1. Read `username`/`password` from context (isolated account). Fail if missing.
2. `fn_login(page, context, username, password)` — UI login (reuses `tests/_functions/login`).
3. Store `context["nc"] = {"seq": <epoch>}` for tests to derive unique code names + titles.

No notification template is created here — each test creates its own customized v3 template
via the shared `notifications_helpers` v3 API with the directory token.
