# CP Multi-Booking — Summary Component Displays Correctly

## Objective
As an anonymous client, open the business livesite, pick "Schedule Now", schedule a
multi-booking appointment with two services (service1 + service2), verify the booking summary
component shows the combined location, duration, and providing staff; complete the booking
with client details; verify the booking confirmation; then verify the client-portal meeting
page shows the first service with state "Pending approval" and the second service as a
linked booking.

## Prerequisites
- Category setup ran: client + service1 (20m) + service2 (40m) + staff + CP multi booking enabled.

## Steps
1. Open the business livesite and pick the "Schedule Now" action (opens the CP scheduler).
2. In the scheduler services page, select `service1` and `service2`, then confirm the selection.
3. On the calendar page, pick the default (first) timeslot and continue (multi-booking confirm).
4. Verify the summary component displays:
   - meeting location: "At TLV"
   - meeting duration: "Duration: 1 hour"
   - providing staff: "With Automation test business"
   - meeting date and start time are present (default values).
5. Fill the intake form with client details (first name "jimmy", last name "slipping",
   email) and confirm the booking.
6. Verify the booking confirmation displays the title "Booking request sent!".
7. Open the client-portal dashboard, open the bookings list, and open the `service1` meeting.
8. Verify the meeting page shows:
   - meeting name: `service1`
   - meeting state: "Pending approval"
   - linked bookings include: `service2`

## Expected Result
- The multi-booking summary shows the combined duration (1 hour), the "At TLV" location, and
  the default staff; the booking is confirmed ("Booking request sent!"); the meeting page
  shows service1 pending approval, linked to service2.
