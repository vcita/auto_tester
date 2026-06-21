# Setup — Notification Center

Mirrors the shared prerequisite of every legacy `notification_center.feature` scenario
(`Given user logged in to automatic account`):

1. Log in to the isolated automatic account via the UI.

No data is created here — each test creates its own notification template (via API) with
the token kind that scenario uses (app token, directory token, or core_internal_app token),
matching the legacy per-scenario setup.
