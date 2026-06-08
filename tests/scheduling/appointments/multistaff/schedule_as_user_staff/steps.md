# Schedule a meeting as a user staff (schedule_as_user_staff)

Migrated from `automation-js/features/tempo/multistaff.feature` (VCITA2-13950),
scenario "Schedule a meeting as a user staff".

Prerequisite (from `_setup`): a fresh multistaff account with two staff (`user_staff`,
`manager_staff`), the client `rina success`, and the service `r2p_appointment` (assigned
to owner + both staff).

## WHAT the test verifies

1. **Switch logged-in staff (API/SSO)** — switch the browser session to `user_staff`
   (SSO token + partner SSO login), mirroring the legacy `switching logged in staff via API`.
2. **Schedule an appointment (UI)** — as `user_staff`, schedule a new appointment for
   `r2p_appointment` / `rina success` (no explicit staff selection — assigned staff
   defaults to the logged-in `user_staff`).
3. **Assert the meeting (UI)** — the meeting page shows:
   - service `r2p_appointment`,
   - client `rina success`,
   - assigned staff = `user_staff`,
   - price `$1.00` (USD).

## In scope (UI) vs prerequisite (API)

- UI (in scope): scheduling via the BO dialog and the meeting-page assertions.
- API (prerequisite): the staff switch is SSO-based (legacy used the SSO API), and the
  meeting id is resolved with a bookings GET (as the legacy `addBookingToContext` did)
  only to open the correct meeting page.
