# Appointments list page — empty / one / two / filtered (list_states)

Migrated from `automation-js/features/tempo/appointments-list.feature` (VCITA2-13953),
scenario 1 ("Appointment list page - empty, with results, and filtered"). The legacy
scenario is tagged `@unstable` (fenv issue VCITA2-3361); it is migrated in full and run
on integration, with the client-portal conversation check hardened by a bounded poll.

The appointments-list rows render `<service title> <STATUS>`; each case asserts the
rendered list against the expected rows (the legacy assertion intent).

## Objective
Verify the appointments list page across four states: empty, one SCHEDULED appointment,
two appointments (SCHEDULED + COMPLETED) plus the client-portal "Appointment confirmed"
conversation, and the COMPLETED status filter.

## Prerequisites
- From `_setup`: logged in on a fresh account with one client and one appointment service
  (`context["appointments_list"]`).

## Steps
1. Open the appointments list page and search with no filter; verify the list is empty.
2. Schedule an appointment via API (the service + client, default future date so it is
   SCHEDULED); search and verify the list shows exactly `<service> SCHEDULED`.
3. Schedule a second appointment via API with the date in the previous month (so it
   lands in the past → COMPLETED). Then:
   a. Open the client's client portal and verify the conversation includes the title
      `Appointment confirmed: <service>`.
   b. Search and verify the list shows `<service> SCHEDULED` and `<service> COMPLETED`
      (future-first ordering).
4. Apply the COMPLETED appointment-status filter; verify only `<service> COMPLETED` shows.

## Expected Result
- Empty search → no rows.
- After one future appointment → `["<service> SCHEDULED"]`.
- After one past appointment → CP conversation title `Appointment confirmed: <service>`
  and list `["<service> SCHEDULED", "<service> COMPLETED"]`.
- COMPLETED filter → `["<service> COMPLETED"]`.

## In scope (UI) vs prerequisite (API)
- UI (in scope): the appointment-list search / state-filter / empty-state assertions, and
  the client-portal "Appointment confirmed" conversation check.
- API (prerequisite, mirrors legacy `user schedules new appointment via API`): scheduling
  the two appointments.
