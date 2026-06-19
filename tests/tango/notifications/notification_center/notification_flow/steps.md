# Notification Center Pane And Badge Flow

Migrated from `automation-js/features/tango/notification_center.feature` — Scenario 1
("Create notification template + notification flow").

## Preconditions (API)
- An app `automationjs<seq>` is created (admin) and assigned to the account; an app token
  is generated for it.
- A notification template `auto_notification<seq>` is created via the app token:
  type `messages`, channel `{pane: true}`, deep link `app/clients`, text (en)
  title "Check this out!", body "Hi ${first_name} ${last_name}! A new message is available",
  display_name "Automation Notification <seq>", description "Notification Description".

## Steps
1. Open the notification pane (toolbar badge). Verify the "last 30 days" empty state shows.
   Close the pane.
2. The app sends a notification to the current (owner) staff with params
   `first_name=auto, last_name=notification`. Verify the badge counter reads "1".
3. Open the notification pane. Verify the notification displays with title "Check this out!",
   body "Hi auto notification! A new message is available", timestamp "Just now", status unread.
   Verify the badge counter no longer shows (opening the pane resets it). Close the pane.
4. Click on the notification. Verify the user is redirected to the new Clients page
   (the template's `app/clients` deep link).
5. Open the notification pane. Verify the notification is "read".
6. Set the notification as unread (blue dot). Verify it is "unread". Then set it as read.
   Verify it is "read".
7. The app sends 3 more notifications to the current staff (Notification 1, Notification 2,
   Notification 3). Verify the badge counter reads "3". Open the pane and verify it displays
   4 notifications total.
8. Toggle ON "only unread" — verify 3 notifications show. Toggle OFF — verify 4 show.
   Mark all notifications as read, then toggle ON "only unread" — verify the
   "all notifications read" empty state shows.
9. Create a staff "Staff Admin" (admin role) via API. The app sends a notification to the
   CURRENT (owner) staff. Verify the badge counter reads "1". Impersonate "Staff Admin"
   (UI). Verify the badge counter does not show. Open the pane and verify the "last 30 days"
   empty state shows (notifications are per-staff; the new staff sees none).
