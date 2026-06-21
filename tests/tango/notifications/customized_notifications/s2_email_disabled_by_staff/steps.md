# Customized Email Notification Disabled By Staff (v3)

Migrated from `automation-js/features/tango/customized-email-notification.feature` —
Scenario 2 ("Customized email notification is disabled by staff").

## Preconditions (API, directory token)
- A customized v3 notification template `new_auto_notification<seq>` is created via the
  directory token: category `payments`, `configurable_by_staff: true`,
  title (en) "Customized Email Notification <seq>",
  description (en) "This is a test notification template.",
  content = email channel (subject "Email Subject", main_title "Main Title For ${name}",
  main_text "Main Text"). No staff_portal block.

## Steps
1. Ensure the account-owner session, then open the Notification Center settings page. Verify
   the notification shows with display_name "Customized Email Notification <seq>" and
   description "This is a test notification template."
2. Uncheck the email channel for the notification (in settings) and save.
3. Refresh the page (re-navigate to settings) and verify the email channel setting persists
   as false.
4. The directory sends the notification to the current (owner) staff via the v3 API with
   params name="Business Name". Verify the email channel is NOT delivered (its channel status
   stays empty) because the staff disabled the email channel.

   Note: the legacy scenario asserted the SEND itself failed. On the current backend the send
   returns 201 but does not dispatch the disabled channel (email status stays empty vs
   "in_progress" when enabled), so the migrated test asserts the behavior-equivalent outcome —
   the staff-disabled channel is not delivered. See changelog.

