# Create Group Event

## Objective
Create a new group event service (class/workshop) with name, duration, price per participant, and maximum capacity to verify group event creation functionality.

## Prerequisites
- User is logged in (from category _setup which calls login function)
- Browser is on Settings > Services page (from delete_service test in execution order)

## Test Data
- Service name: "Test Group Workshop {timestamp}"
- Duration: 1 hour (default)
- Price: 25 (ILS)
- Max attendees: 10
- Location: Face to face (My business address)
- Description: "Group workshop for testing purposes."

## Steps

1. Verify on Services page
   - URL should contain "/app/settings/services"
   - Services list should be visible

2. Open "New service" dropdown menu
   - Click the "New service" button with dropdown arrow

3. Select "Group event" from dropdown menu
   - Click the "Group event" menu item

4. Wait for group event creation dialog
   - Dialog with title "New service - Group event" should appear

5. Fill service name
   - Enter "Test Group Workshop {timestamp}" in service name field
   - save_to_context: created_group_event_name

6. Set max attendees
   - Enter "10" in the max attendees field

7. Select location as "Face to face"
   - Click "Face to face" location button
   - Default "My business address" radio should be selected

8. Set price with fee
   - Click "With fee" button
   - Enter "25" in the price field

9. Click Create button
   - Wait for dialog to close

10. Handle event times dialog (CONDITIONAL)
    - This dialog appears ONLY on first group event creation for an account
    - If dialog appears: Click "I'll do it later" button
    - If dialog doesn't appear: Continue to next step
    - Test handles both cases automatically

11. Refresh services list (workaround for UI bug)
    - Navigate to Settings main page
    - Navigate back to Services
    - Note: This is a known UI bug where list doesn't refresh after creation

12. Verify group event appears in list
    - Find the group event by name in services list
    - Verify it shows "10 attendees" (not "1 on 1")
    - save_to_context: created_group_event_id (from URL after clicking)

13. Add description via advanced edit
    - Click on the group event to open edit page
    - Enter description in description field
    - Click Save

14. Navigate back to services list
    - Return to Settings > Services page for next test

## Expected Result
- Group event is created with correct name, duration, price, and max attendees
- Group event appears in services list showing "10 attendees"
- Description is saved successfully

## Context Updates
- created_group_event_id: ID of the created group event
- created_group_event_name: Name of the group event
- created_group_event_description: "Group workshop for testing purposes."
- created_group_event_duration: 60 (minutes)
- created_group_event_price: 25
- created_group_event_max_attendees: 10

## Notes
- Group events differ from 1-on-1 services by having "Max attendees" field
- After creation, vcita prompts to enter event dates/times (we skip this)
- Known UI bug: services list doesn't auto-refresh after creation
