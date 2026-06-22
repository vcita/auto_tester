# View Appointment Test

## Objective

Open and view the details of an existing appointment from the business calendar.

## Prerequisites

- User is logged in
- An appointment exists (from create_appointment test: `created_appointment_client`, `created_appointment_service`)
- Browser is on the Calendar page

## Test Data

- Client: Use `created_appointment_client` from context
- Service: Use `created_appointment_service` from context

## Steps

1. Verify we're on the Calendar page
2. Locate the appointment in the calendar grid (by client name)
3. Click on the appointment to open the details panel/dialog
4. Verify the appointment details are displayed:
   - Client name matches `created_appointment_client`
   - Service name matches `created_appointment_service`
   - Date and time are shown
5. Close the appointment details view

## Success Criteria

- Appointment details panel/dialog opens successfully
- Client name is visible and correct
- Service name is visible and correct
- Details view can be closed
