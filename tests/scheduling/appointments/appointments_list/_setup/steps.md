# Setup — Appointments List page (isolated account)

Mirrors the legacy appointments-list.feature Background:
`user logged in to "appointments list" page in automatic account via API` +
`user creates new client via API` + `user creates new service via API`.

## Objective
Prepare a fresh isolated account with one client and one appointment service so the
appointments list page tests run against a deterministic, empty starting list.

## Steps
1. Log in to the fresh isolated account (UI session for the tests that follow).
2. Create one client via API (`first last`, `test+<seq>@vmeetme.com`); capture the
   client-portal token (used by the CP "Appointment confirmed" conversation check).
3. Create one appointment service via API (`service<seq>`), confirmed with an
   independent GET read-back before the tests rely on it.

## Expected Result
- A logged-in session on a fresh account with exactly one client and one appointment
  service, and no bookings yet (so the empty-state assertion is real).

## Context Updates
- Save `appointments_list` = `{client, service}` for the tests in this subcategory.

No appointments are scheduled here — appointment scheduling is legacy API setup done
inside `list_states` (interleaved with the list assertions, as in the legacy scenario).
