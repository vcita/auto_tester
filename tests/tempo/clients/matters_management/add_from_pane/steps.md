# Add Matter From Contact Pane

## Objective
Verify a user can add a new matter under a contact from the contact's matter page
(contact-pane Add matter action), and that the matter appears under that contact.

## Prerequisites
- From `_setup`: logged in; `contact_client_id` / `contact_client_email` exist.

## Steps
1. Open the contact's matter page (the "contact client" contact).
2. Use the contact-pane "Add matter" action to start adding a matter under this contact.
3. Confirm/continue the suggested contact details.
4. Enter the matter name `matter_1` and save.
5. Verify the matter list now contains `matter_1`.
6. Verify the displayed contact email matches the "contact client" email.

## Expected Result
- The matter list under the contact contains `matter_1`.
- The contact shown is the "contact client" (email matches).

## Context Updates
- Save `contact_client_id` is reused by later tests (no new context needed).
