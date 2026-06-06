# Setup — Sales Widget (isolated account)

Mirrors the legacy sales_widget.feature Background on a fresh isolated account.

1. Enable the `new_dashboard` feature flag (before login) so the dashboard renders the Sales widget.
2. Log in to the isolated account (UI session is needed for the dashboard views).

No context entities are created here; each test seeds its own data.
