# Delete Group Event

## Objective
Delete the test group event to clean up test data and verify group event deletion functionality.

## Prerequisites
- User is logged in (from category _setup)
- Group event exists with context variables from create_group_event test:
  - created_group_event_id
  - created_group_event_name
- Browser is on Services page (from edit_group_event test)

## Steps

1. Verify on Services page
   - URL should contain "/app/settings/services"
   - Services list should be visible

2. Find and click on the test group event
   - Locate group event by name: {context.created_group_event_name}
   - Click to open edit page

3. Wait for edit page to load
   - Service name field should be visible

4. Click Delete button
   - Click the "Delete" button in the header toolbar

5. Confirm deletion in dialog
   - Dialog should appear: "Are you sure you want to delete this service?"
   - Click "Ok" button to confirm

6. Wait for redirect to services list
   - URL should return to "/app/settings/services"

7. Verify group event was deleted
   - Search for group event by name in list
   - Should NOT be found (count = 0)

## Expected Result
- Group event is removed from the services list
- Group event cannot be found after deletion
- Browser returns to services list

## Context Cleanup
Clear all group event context variables:
- created_group_event_id
- created_group_event_name
- created_group_event_description
- created_group_event_duration
- created_group_event_price
- created_group_event_max_attendees
- edited_group_event_duration
- edited_group_event_price
- edited_group_event_max_attendees

## Notes
- This is the last test in the group events series
- Cleans up test data to leave system in clean state
- Delete button is on the edit page header (same location as regular services)
- Confirmation dialog requires clicking "Ok" (not "Confirm" or "Yes")
