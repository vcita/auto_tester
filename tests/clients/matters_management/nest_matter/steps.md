# Nest Existing Matter Under Contact

## Objective
Verify a user can nest an existing standalone matter ("matter client") under a
contact ("contact client") via the matter More menu, and that the nested matter
appears under the contact with the correct page title.

## Prerequisites
- From `_setup`: logged in; `matter_client_id`, `matter_client_name`,
  `contact_client_name`, `contact_client_email` exist.

## Steps
1. Open the "matter client" matter page.
2. Open the matter More menu and choose the nesting action.
3. In the nesting dialog, search for the "contact client" and select it, then submit.
4. Verify the matter list contains the "matter client".
5. Verify the displayed contact email matches the "contact client" email.
6. Verify the page title shows "matter client".

## Expected Result
- The matter list under the contact contains "matter client".
- The contact shown is the "contact client" (email matches).
- The page title shows "matter client".

## Context Updates
- None (uses existing context).
