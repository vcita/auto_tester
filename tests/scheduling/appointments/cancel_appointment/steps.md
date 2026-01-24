# Cancel Appointment Test

## Objective

Cancel an existing appointment from the business calendar. This verifies that business owners can cancel an appointment that was previously created.

## Prerequisites

- User is logged in
- An appointment exists (from create_appointment test)
- Context has: created_appointment_client, created_appointment_service

## Test Data

- Client: Use `created_appointment_client` from context

## Steps

1. Navigate to Calendar if not already there
2. Wait for calendar to load and find the appointment
3. Click on the appointment to open details
4. Wait for appointment details page to load
5. Click "Cancel Appointment" button
6. Confirm the cancellation in the dialog
7. Verify the appointment status changes to "Canceled"
8. Verify the appointment no longer appears in calendar (or appears as canceled)
9. Return to calendar

## Success Criteria

- Appointment is successfully canceled
- Status shows "Canceled" in the appointment details (actual data verification)
- No errors during the process
