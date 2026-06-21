# Create And Send Customized Email Notification (v3)

Migrated from `automation-js/features/tango/customized-email-notification.feature` —
Scenario 1 ("Create and send customized email notification").

## Preconditions (API, directory token)
- A customized v3 notification template `new_auto_notification<seq>` is created via the
  directory token: category `payments`, `configurable_by_staff: true`,
  title (en) "Customized Email Notification <seq>",
  description (en) "This is a test notification template.",
  content = email channel with subject "Email Subject", main_title "Main Title For ${name}",
  main_text "Main Text", primary CTA button text "Primary CTA Button", and a staff_portal
  block (title "Hello, ${name}", message_body "Welcome").

## Steps
1. Ensure the account-owner session, then open the Notification Center settings page. Verify
   the notification shows with display_name "Customized Email Notification <seq>" and
   description "This is a test notification template."
2. The directory sends the notification to the current (owner) staff via the v3 API with
   params name="Business Name". Verify the send succeeded (a notification uid is returned).
3. Verify the sent v3 notification exists (GET by uid returns data).
4. The directory updates the template via the v3 API: new title
   "Customized Email Notification Updated Title <seq>" and a new primary CTA button text
   "Primary CTA Button update name".
5. Refresh the page (re-navigate to settings) and verify the notification now shows with
   display_name "Customized Email Notification Updated Title <seq>" and the same description.
6. Go to the dashboard and verify the notification badge counter reads "1".
7. Verify the v3 email notification status contains "processed".
