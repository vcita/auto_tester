# Create Custom Appointment Test

## Objective

Create a custom 1-on-1 appointment without using a predefined service. This allows business owners to book a meeting with a client that doesn't fit any existing service template.

## Prerequisites

- User is logged in
- Test client exists (from context: created_client_name)

## Test Data

- Client: Use `created_client_name` from context
- Custom meeting title (will be generated)

## Steps

1. Navigate to Calendar if not already there
2. Wait for calendar to load
3. Click "New" button to open creation menu
4. Select "Appointment" from dropdown
5. Wait for client selection dialog
6. Search for and select the test client
7. Select "Custom meeting" option (instead of a predefined service)
8. Fill in custom meeting details (title)
9. Click "Schedule appointment"
10. Verify appointment appears in calendar

## Success Criteria

- Appointment is created with custom meeting (no predefined service)
- Appointment appears in calendar with the client name (actual data verification)
- No errors during the process
