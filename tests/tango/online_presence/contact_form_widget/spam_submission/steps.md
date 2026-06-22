# Spam Client Contact Form Submission

Migrated from `automation-js/features/tango/contact-form-widget.feature`
(Scenario: "spamming client fills up contact form").

## Preconditions (setup)
- Logged in to the isolated automatic account.
- A target client (`first last`, `test+<seq>@vmeetme.com`) exists (created via API).

## Steps
1. Mark the target client as spam from the client card.
2. As a public visitor, submit the contact-form widget using the spam client's
   details (same first/last/email) and a message ("hello").
3. Open the client's conversation.

## Expected
- The business receives **no message** from the spam client — the client's
  conversation is empty.
