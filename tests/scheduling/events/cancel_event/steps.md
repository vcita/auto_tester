# Cancel Event Test

## Objective
Cancel a scheduled group event instance.

## Prerequisites
- User is logged in
- A scheduled event exists (context: scheduled_event_id)
- Browser is on event detail page or Calendar page

## Steps
1. Open the scheduled event
2. Click "Cancel" or "Cancel event" button
3. Confirm cancellation if prompted
4. Verify event is marked as cancelled or removed from calendar
5. Clear event context variables

## Expected Result
- Event is cancelled successfully
- Event is marked as cancelled or removed from active calendar
- Context variables are cleared (scheduled_event_id, scheduled_event_time, event_attendee_id)
