# Add Matter From Quick Actions

## Objective
Verify a user can add a new matter under an existing contact via the Quick Actions
menu (suggested-contact flow), and that the matter appears under that contact.

## Prerequisites
- From `_setup`: logged in; `contact_client_email` exists.
- `add_from_pane` has run (the contact already has `matter_1`).

## Steps
1. Open the Quick Actions menu and choose Add client/matter.
2. In the dialog, search the contact by email and select the "contact client".
3. Choose to create a new client under this contact and continue.
4. Enter the matter name `matter_2` and save.
5. Open the contact's matter page and verify the matter list contains `matter_2`.
6. Verify the displayed contact email matches the "contact client" email.

## Expected Result
- The matter list under the contact contains `matter_2`.
- The contact shown is the "contact client" (email matches).

## Context Updates
- None (uses existing context).
