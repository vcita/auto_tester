# Edit Appointment Test

## Objective

Edit the notes/details of an existing appointment from the business calendar. This test verifies that business owners can add notes to an appointment that was created.

## Prerequisites

- User is logged in
- An appointment exists (from create_appointment test)
- Context has: created_appointment_client, created_appointment_service

## Test Data

- Client: Use `created_appointment_client` from context
- Service: Use `created_appointment_service` from context
- Notes: "Test note added at {timestamp}"

## Steps

1. Navigate to Calendar if not already there
2. Wait for calendar to load and find the appointment
3. Click on the appointment to open details
4. Wait for appointment details page to load
5. Find and click the "Add note" or "Notes" section
6. Enter test note text
7. Save the note
8. Verify the note appears in the appointment details
9. Return to calendar

## Success Criteria

- Note is successfully saved to the appointment
- Note text is visible in the appointment details (actual data verification)
- No errors during the process
