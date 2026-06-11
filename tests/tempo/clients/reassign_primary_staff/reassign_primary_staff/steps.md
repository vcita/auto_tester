# Reassign Matter Primary Staff

Migrated from `automation-js/features/steps/reassign-matter-primary-staff.feature`
(scenario "user sets a new primary staff member to a client").

## Goal

Reassign a matter's primary staff to a second staff member and confirm both the
appointment reassignment and the assignment-notification email.

## Preconditions (created via API on the isolated auto-account)

- A second staff member **Staff B** exists.
- A client **first last** exists.
- A free appointment service **test_service** exists.
- An appointment for **test_service** is scheduled for **first last**, assigned to
  the account owner (the original primary staff) — not Staff B.
- The browser is logged in to the same auto-account.

## Steps

1. Open the client (matter) page for **first last**.
2. Open the matter primary-staff editor.
3. Change the primary staff to **Staff B**.
4. Choose to also reassign the matter's existing appointments to the new assignee.
5. Save the change.

## Expected results

1. In the matter's Bookings list, the **test_service** appointment is assigned to **Staff B**.
2. The business receives an email with the subject **"first last was assigned to you"**.
