# Add Attendee Test

## Objective
Add a client as an attendee to a scheduled group event.

## Prerequisites
- User is logged in
- A scheduled event exists (context: scheduled_event_id)
- A test client exists (context: event_client_name)
- Browser is on Calendar page or event detail page

## Steps
1. Open the scheduled event (navigate to event detail if not already open)
2. Find "Add attendee" or "Add client" button/option
3. Search for the test client (from context)
4. Select the client
5. Confirm/add the attendee
6. Verify client appears in attendees list

## Expected Result
- Client is added as attendee
- Client appears in the attendees list
- Context contains:
  - event_attendee_id: ID of the client added to event
