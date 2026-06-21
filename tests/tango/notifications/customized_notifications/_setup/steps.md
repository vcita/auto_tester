# Setup — Customized Notifications

Mirrors the shared prerequisite of every legacy `customized-email-notification.feature`
scenario (`Given user logged in to automatic account via API`):

1. Log in to the isolated automatic account via the UI.

No data is created here — each test creates its own customized notification template via the
v3 communication API (directory token), matching the legacy per-scenario setup.
