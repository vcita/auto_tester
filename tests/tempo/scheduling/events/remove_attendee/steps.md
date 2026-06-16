# Remove Attendee Test

## Objective
Remove a client from a scheduled group event's attendee list.

## Prerequisites
- User is logged in
- A scheduled event exists (context: scheduled_event_id)
- An attendee exists on the event (context: event_attendee_id)
- Browser is on event detail page

## Steps
1. Open the scheduled event (verify on event detail page)
2. Find the attendee in the attendees list
3. Click remove/delete button for the attendee
4. Confirm removal if prompted
5. Verify attendee is removed from the list

## Expected Result
- Attendee is removed from the event
- Attendee no longer appears in attendees list
- Event still exists and is accessible
