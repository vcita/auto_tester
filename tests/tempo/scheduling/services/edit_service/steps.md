# Edit Service

## Objective
Edit an existing service to modify its duration and price, verifying that changes are saved correctly.

## Prerequisites
- User is logged in (from category _setup)
- Service exists with `created_service_id` in context (from create_service test)

## Test Data
- New duration: 45 minutes (changed from 30)
- New price: $75 (changed from $50)

## Steps

1. Verify we're on the Services page
   - Should already be on Services page from previous test
   - If not, navigate to Settings > Services

2. Find and click on the test service
   - Locate service by name (from context: `created_service_name`)
   - Click to open service edit form/dialog

3. Modify service details
   - Change duration from 30 to 45 minutes
   - Change price from $50 to $75

4. Save changes
   - Click Save button
   - Wait for confirmation/success message

5. Verify changes were saved
   - Re-open the service or check list view
   - Confirm duration shows 45 minutes
   - Confirm price shows $75

## Expected Result
- Service duration is updated to 45 minutes
- Service price is updated to $75
- Changes persist after saving

## Context Updates
- Update `edited_service_duration` = 45
- Update `edited_service_price` = 75

## Notes
- Browser should already be on Services page from create_service test
- Verify changes by re-opening the service details
