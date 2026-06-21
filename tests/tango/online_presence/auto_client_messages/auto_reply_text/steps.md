# Auto Reply Text Change

Migrated from `automation-js/features/tango/auto-client-messages.feature`
(Scenario: "auto reply text change").

## Objective
A business updates the auto-reply message text in settings. When a client leaves
their details via the public livesite contact form, the livesite success page
displays the updated auto-reply message — proving the settings change took effect
end-to-end.

## Preconditions (setup)
- Logged in to the isolated automatic account.

## Steps
1. Open the business settings "Messages & Documents" tab and update the auto-reply
   message text to a custom value ("bla2").
2. As a public visitor, open the business livesite and choose the "Leave details"
   action.
3. Fill the leave-details form (Subject "hi", Message "hello", Email
   "form+<seq>@vmeetme.com", First Name "form_first", Last Name "form_last") and
   submit it.

## Expected
- The livesite success page displays the auto-reply message exactly as configured
  ("bla2").
