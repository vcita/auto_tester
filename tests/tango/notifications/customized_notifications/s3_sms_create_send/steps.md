# Create And Send Customized SMS Notification (v3)

Migrated from `automation-js/features/tango/customized-email-notification.feature` —
Scenario 3 ("Create and send customized SMS notification").

## Preconditions (API, directory token)
- A customized v3 notification template `new_auto_notification<seq>` is created via the
  directory token: category `payments`, `configurable_by_staff: true`,
  title (en) "Customized SMS Notification <seq>",
  description (en) "This is a test notification template.",
  content = sms channel with message_body "SMS Message Body with ${name}".

## Steps
1. Ensure the account-owner session, then open the Notification Center settings page. Verify
   the notification shows with display_name "Customized SMS Notification <seq>" and
   description "This is a test notification template."
2. Check (enable) the SMS channel for the notification (in settings) and save.
3. The directory sends the notification to the current (owner) staff via the v3 API with
   params name="Business Name". Verify the send succeeded (a notification uid is returned).
4. Verify the v3 sms notification status contains "in_progress".
