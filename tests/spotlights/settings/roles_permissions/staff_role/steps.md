# Staff Role Management

## Objective
Verify that an admin can open a staff member's role page, see the staff's current
role, change it, and have the change reflected in the staff list.

## Prerequisites
- Logged in to the isolated account (from subcategory `_setup`).
- A staff member "user_staff" with role "User" exists (created in `_setup`).

## Steps
1. Open the staff list and choose "Edit staff permissions" for "user_staff".
2. Verify the staff role page shows the staff name "user_staff" and role "User".
3. Change the staff's role to "Manager".
4. Open the staff list again.

## Expected Result
- The staff role page opens showing name "user_staff" and current role "User".
- After changing the role, the staff "user_staff" appears in the staff list with
  role "Manager".

## Context Updates
- None.
