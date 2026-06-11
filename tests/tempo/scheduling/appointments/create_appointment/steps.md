# Create Appointment Test

## Objective

Manually create a 1-on-1 appointment for a client using a predefined service from the business calendar.

## Prerequisites

- User is logged in
- A test service exists (from _setup: `created_service_name`)
- A test client exists (from _setup: `created_client_name`)
- Browser is on the Calendar page

## Test Data

- Client: Use `created_client_name` from context
- Service: Use `created_service_name` from context
- Date: Today or next available day
- Time: Default (next available slot)

## Steps

1. Verify we're on the Calendar page
2. Click "New" button to open the menu
3. Select "Appointment" from the dropdown menu
4. In the client search dialog, search for the test client by name
5. Click on the test client to select them
6. In the service selection panel, search for the test service
7. Click "Select" on the test service
8. Keep default date/time settings
9. Click "Schedule appointment" button
10. Verify the appointment appears in the calendar view

## Success Criteria

- Appointment is created successfully
- Appointment visible in calendar grid (actual data verification)
