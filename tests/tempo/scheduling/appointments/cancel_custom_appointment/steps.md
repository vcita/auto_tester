# Cancel Custom Appointment Test

## Objective

Cancel a custom appointment (appointment without predefined service) from the business calendar. This verifies that business owners can cancel a custom appointment that was previously created.

## Prerequisites

- User is logged in
- A custom appointment exists (from create_custom_appointment test)
- Context has: created_custom_appointment_client, created_custom_appointment_title

## Test Data

- Client: Use `created_custom_appointment_client` from context

## Steps

1. Navigate to Calendar if not already there
2. Wait for calendar to load and find the custom appointment
3. Click on the appointment to open details
4. Wait for appointment details page to load
5. Click "Cancel Appointment" button
6. Confirm the cancellation in the dialog
7. Verify the appointment status changes to "Canceled"
8. Return to calendar

## Success Criteria

- Custom appointment is successfully canceled
- Status shows "Canceled" in the appointment details (actual data verification)
- No errors during the process

## Context Operations

Reads from context:
- `created_custom_appointment_client`: Client name to find the appointment

Clears from context after successful cancellation:
- `created_custom_appointment_client`
- `created_custom_appointment_title`

## Notes

- This test follows the same pattern as `cancel_appointment` but for custom appointments
- Custom appointments don't have a service, so we identify them by client name
- Cancelled appointments remain in the system with "Cancelled" status (this is acceptable - appointments cannot be deleted, only cancelled)
