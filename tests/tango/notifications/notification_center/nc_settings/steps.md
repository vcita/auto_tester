# Notification Center Settings

Migrated from `automation-js/features/tango/notification_center.feature` — Scenario 2
("Notification Center Settings").

## Preconditions (API, directory token)
- A notification template `auto_nc_settings<seq>` is created via the directory token:
  type `payments`, channel `{pane: true, push: true}`, deep link `app/clients`,
  text (en) title "Check this out!", body "Hi! A new message is available",
  display_name "Automation NC Settings <seq>", description "Notification description",
  `show_in_settings: false`.

## Steps
1. Open the Notification Center settings page. Verify the notification does NOT show
   (because `show_in_settings` is false).
2. The directory updates the template to `show_in_settings: true`. Refresh the page and
   verify the notification now shows with display_name "Automation NC Settings <seq>" and
   description "Notification description". Verify its settings: push = true, pane = true.
3. The directory updates the template channel to `{push: false}`. Refresh the page and
   verify the settings: push = hidden, pane = true.
4. Open the notification settings (via the pane's settings button). Verify the notification
   settings page is displayed.
5. The directory sends the notification to the current staff. Verify the badge counter reads
   "1". Open the pane and verify the notification displays with title "Check this out!",
   body "Hi! A new message is available", timestamp "Just now", status unread.
6. Uncheck the pane channel for the notification (in settings). The directory sends the
   notification again. Verify the badge counter does not show (pane delivery is suppressed).
