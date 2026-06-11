# Edit Group Event

## Objective
Edit an existing group event to modify its duration, price, and max attendees, verifying that changes are saved correctly.

## Prerequisites
- User is logged in (from category _setup)
- Group event exists with context variables from create_group_event test:
  - created_group_event_id
  - created_group_event_name
- Browser is on Services page (from create_group_event test)

## Test Data
- New duration: 90 minutes (1 hour 30 min, changed from 60 min)
- New price: 35 (changed from 25)
- New max attendees: 15 (changed from 10)

## Steps

1. Verify on Services page
   - URL should contain "/app/settings/services"
   - Services list should be visible

2. Find and click on the test group event
   - Locate group event by name: {context.created_group_event_name}
   - Click to open edit page

3. Wait for edit page to load
   - Service name field should be visible
   - Verify "Service type" shows "Group event"

4. Change max attendees from 10 to 15
   - Click on max attendees field
   - Clear and enter "15"

5. Change duration to 1 hour 30 minutes
   - Click on Minutes dropdown (currently "0 Minutes")
   - Select "30 Minutes" option

6. Change price from 25 to 35
   - Click on price field
   - Clear and enter "35"

7. Save changes
   - Click Save button
   - Wait for page to refresh

8. Verify changes were saved on edit page
   - Max attendees should show "15"
   - Minutes should show "30 Minutes"
   - Price should show "35"

9. Navigate back to services list
   - Click Settings in sidebar
   - Click Services button

10. Verify group event exists in services list
    - Find group event by name
    - Verify it is visible in the list
    - Note: Changes were already verified in Step 8 on the edit page

## Expected Result
- Group event duration is updated to 90 minutes (1h 30m)
- Group event price is updated to 35
- Group event max attendees is updated to 15
- Changes persist after saving and re-opening

## Context Updates
- edited_group_event_duration: 90 (minutes)
- edited_group_event_price: 35
- edited_group_event_max_attendees: 15

## Notes
- Edit page is the same for group events and 1-on-1 services
- Group events have the additional "Max attendees" field
- Duration is split into Days, Hours, and Minutes dropdowns
