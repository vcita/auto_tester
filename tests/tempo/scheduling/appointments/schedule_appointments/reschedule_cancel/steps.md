# Reschedule And Cancel Appointment

Migrated from `scheduling-appointments.feature` scenario 3 ("reschedule and cancel appointment").
Zero scope loss: schedule a past (COMPLETED) appointment, reschedule it to next week
(SCHEDULED), then cancel it (CANCELLED), verifying state and times at each step.

## Preconditions (from `_setup`)

- Isolated account, logged in as owner.
- `service1` appointment service and client `Chuck Norris` exist (API).

## Steps

1. Schedule an appointment from the BO calendar:
   - service `service1`, existing client `Chuck Norris`,
   - meeting date `previous_month` (day 10 — in the past),
   - start time `01:00 AM`, end time `05:00 AM`.
2. **Verify** the created meeting: name `service1`, client `Chuck Norris`,
   state `COMPLETED`, start `1:00 AM`, end `5:00 AM`.
3. Reschedule the appointment from the detail page (Kendo datetime dialog):
   - new date `next_week`, start `3:00am`, end `4:00am`.
4. **Verify**: state `SCHEDULED`, start `3:00 AM`, end `4:00 AM`, and a "Rescheduled from" note.
5. Cancel the appointment from the detail page.
6. **Verify**: state `CANCELLED`, times unchanged (`3:00 AM` / `4:00 AM`).

## Notes

- The schedule wizard is a Vue app (`#vue_iframe_layout`) nested in the Angular iframe
  (`iframe[title="angularjs"]`); the reschedule/cancel dialogs and the detail page render in
  the outer Angular iframe.
- A past start time makes the meeting `COMPLETED`; rescheduling into the future makes it
  `SCHEDULED` (legacy state rules from `createMeetingDialog` / `appointment.js`).
