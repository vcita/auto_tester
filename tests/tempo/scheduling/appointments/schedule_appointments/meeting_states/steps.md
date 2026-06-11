# Schedule Appointments With Different Meeting States

Migrated from `scheduling-appointments.feature` scenario 1 ("Schedule from bo: new client &
staff flows, meeting states"). Zero scope loss: schedule three appointments from the BO that
exercise inline new-client / new-staff creation and the three meeting states.

## Preconditions (from `_setup`)

- Isolated account, logged in as owner; `service1`, staff `user_staff`, and the manager staff
  `optimus_prime` (assigned to `service1`) exist.

## Steps

1. Schedule `service1` creating a **new client** "rick morty" inline, assigning the existing
   `user_staff`, and **requesting client confirmation** -> state **INVITED**.
   Verify: name `service1`, client `rick morty`, assigned staff `user_staff`, state INVITED.
2. Schedule `service1` for the now-existing `rick morty`, assigning the manager staff
   `optimus_prime`, on `next_month` (day 10), all-day, 01:00 AM - 05:00 AM -> state **SCHEDULED**.
   Verify: assigned staff `optimus_prime`, state SCHEDULED, date ~ next month / day 10.
3. Schedule `service1` for `rick morty`, assigning the manager staff `optimus_prime`, on
   `previous_month` (day 10, in the past) -> state **COMPLETED**.
   Verify: assigned staff `optimus_prime`, state COMPLETED, date ~ previous month / day 10.

## Notes

- New client uses the Angular "New client" md-dialog opened from the scheduling client picker;
  the email field is an autocomplete dynamic field (click + type).
- **Product-change adaptation:** the legacy scenario created the manager staff *through* the
  scheduling dialog's "create new staff" entry. In the current product that action persists the
  appointment and navigates to the appointment page (the appointment controller now owns
  `add-new-staff`), so it no longer creates a staff inline in the dialog. To preserve the
  scenario's assertions (assigned manager staff on a more-than-a-day next-month meeting) without
  losing the date/state coverage, the manager staff is provisioned via the Platform API in
  `_setup` and selected through the dialog's assigned-staff dropdown.
- Meeting state is derived from the date (past -> COMPLETED, future -> SCHEDULED) and from
  requesting client confirmation (-> INVITED), per the legacy state rules.
