# Multi-staff meeting as the owner (multi_staff_meeting)

Migrated from `automation-js/features/tempo/multistaff.feature` (VCITA2-13950),
scenario "Schedule a multi staff meeting as an admin".

Prerequisite (from `_setup`): logged in as the owner on a fresh multistaff account with
two staff (`user_staff`, `manager_staff`), the client `rina success`, and the service
`r2p_appointment` (assigned to owner + both staff).

## WHAT the test verifies

1. **Schedule with additional staff (UI)** — as the owner, schedule a new appointment for
   `r2p_appointment` / `rina success`, opening the additional-staff picker and selecting
   both `user_staff` and `manager_staff`, then submit.
2. **Remove an additional staff (UI)** — on the created meeting page, edit the additional
   staff and remove `user_staff`.
3. **Assert the meeting (UI)** — the meeting page shows:
   - service `r2p_appointment`,
   - client `rina success`,
   - assigned staff = the business owner (the account owner display name),
   - additional staff = `manager_staff` only (`user_staff` removed).

## In scope (UI) vs prerequisite (API)

- UI (in scope): scheduling via the BO dialog incl. additional-staff multi-select,
  removing an additional staff, and the meeting-page assertions.
- API (prerequisite): the meeting id is resolved with a bookings GET (as the legacy
  `addBookingToContext` did) only to open the correct meeting page.
