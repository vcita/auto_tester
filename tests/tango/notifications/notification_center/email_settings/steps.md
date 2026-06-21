# Email Channel In Notification Center Settings

Migrated from `automation-js/features/tango/notification_center.feature` — Scenario 3
("Email in Notification Center Settings").

## Preconditions (API, core_internal_app token)
- A notification template `auto_nc_email_settings<seq>` is created via the core_internal_app
  token: type `payments`, channel `{pane: true, push: true}`, deep link `app/reports`,
  text (en) title "Check this out!", body "Hi! A new message is available",
  display_name "Automation NC Email Settings <seq>", description "Notification description".

## Steps
1. Open the Notification Center settings page. Verify the notification shows with display_name
   "Automation NC Email Settings <seq>" and description "Notification description". Verify its
   settings: push = true, pane = true, email = hidden (email channel not configured yet).
2. The core_internal_app updates the template channel to `{email: true}`. Refresh the page and
   verify the settings: push = true, pane = true, email = true (the email toggle is now visible
   and on).
