# Collaborators Setup — Steps (WHAT)

Migrated from `add-remove-staff-in-matter.feature` Background.

Prepare an isolated account so the matter-collaborators test can run deterministically:

1. Log in to the isolated automation account.
2. Create two additional staff members: **Staff B** and **Staff C** (role: user).
3. Create one bookable **service**, offered by the owner and **Staff C** (so the
   warning-trigger appointment assigned to Staff C is accepted later).
4. Create the client **"new client"**.

The warning-trigger appointment is created mid-test (after Staff C is a collaborator),
not here — seeding it in setup would auto-add Staff C as a collaborator and break the
test's initial state. See the test's `script.md`.
