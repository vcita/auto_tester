# Schedule Event Test

## Objective
Schedule a group event instance by selecting a date and time for an existing group event service.

## Prerequisites
- User is logged in (from _setup)
- Group event service exists (context: event_group_service_name)
- Browser is on Calendar page (from _setup)

## Steps
1. Verify on Calendar page
2. Click "New" button
3. Select "Group event" from dropdown menu
4. Select the group event service (from context)
5. Choose a date and time (tomorrow, next available slot)
6. Click "Schedule event" or "Save"
7. Verify event appears in calendar

## Expected Result
- Event instance is scheduled successfully
- Event appears in calendar at the selected date/time
- Context contains:
  - scheduled_event_id: ID of the scheduled event instance
  - scheduled_event_time: Date/time of the scheduled event
