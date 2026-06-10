# Appointment With Arrival Window

Migrated from `scheduling-appointments.feature` scenario 4 ("appointment with arrival window").
Zero scope loss: verify the arrival-window value resolution (account default, service override,
in-dialog override, custom, and reschedule override) on both the appointment detail page and the
client notification email.

## Preconditions (from `_setup`)

- Isolated account, logged in as owner; `service1` exists; client `Chuck Norris` exists.
- Business arrival-window value is set to **45 minutes** (account default, set in `_setup`).

## In-test prerequisites (API)

- Create `service2` (appointment service).
- Override `service2` arrival window to **15 minutes**.

## Steps

1. Schedule two appointments on `next_month` at `03:00 PM` for `Chuck Norris`, no in-dialog
   arrival override:
   - `service1` -> arrival window resolves to the account default **3:00 pm - 3:45 pm**.
   - `service2` -> arrival window resolves to the service override **3:00 pm - 3:15 pm**.
   Verify each detail page shows the expected arrival window, and the client receives an email
   containing `Estimated arrival time:` with `3:00 pm - 3:45 pm` and `3:00 pm - 3:15 pm`.
2. Schedule two appointments on `next_month` at `04:00 PM` for `Chuck Norris` with an in-dialog
   arrival override:
   - `service1` arrival `2 hours` -> **4:00 pm - 6:00 pm**.
   - `service2` arrival `Custom 75` (1h 15m) -> **4:00 pm - 5:15 pm**.
   Verify detail pages and client emails (`Estimated arrival time:` + each window).
3. Reschedule the `service1` `2 hours` appointment, changing only the arrival window to
   `30 minutes` -> **4:00 pm - 4:30 pm**.
   Verify the detail page and the client email.

## Notes

- Arrival window in the scheduling dialog is the `.arrival-window-dropdown` select; `Custom`
  reveals hours/minutes sub-selects.
- In the reschedule dialog the arrival window is the `.arrival-window-select` md-select.
- Detail-page arrival window is read from `.arrival-window-time` ("Estimated arrival:").
- Client emails are polled via the automation message-content API (legacy `api/email.js`).
