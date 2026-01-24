# Reschedule Appointment Test

## Objective

Reschedule an existing appointment to a different time slot from the business calendar. This verifies that business owners can change the time of an appointment.

## Prerequisites

- User is logged in
- An appointment exists (from create_appointment test)
- Context has: created_appointment_client, created_appointment_service

## Test Data

- Client: Use `created_appointment_client` from context
- New Time: Move appointment 1 hour later

## Steps

1. Navigate to Calendar if not already there
2. Wait for calendar to load and find the appointment
3. Click on the appointment to open details
4. Wait for appointment details page to load
5. Click "Reschedule" button
6. In the reschedule dialog, select a new time (1 hour later)
7. Confirm the reschedule
8. Verify the appointment time has changed in the details
9. Return to calendar

## Success Criteria

- Appointment is successfully rescheduled to new time
- New time is visible in appointment details (actual data verification)
- No errors during the process
