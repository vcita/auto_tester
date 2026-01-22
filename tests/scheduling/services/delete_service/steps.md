# Delete Service

## Objective
Delete the test service to clean up test data and verify service deletion functionality.

## Prerequisites
- User is logged in (from category _setup)
- Service exists with `created_service_id` in context (from create_service test)

## Steps

1. Verify we're on the Services page
   - Should already be on Services page from previous test
   - If not, navigate to Settings > Services

2. Find the test service
   - Locate service by name (from context: `created_service_name`)

3. Open delete option
   - Click on service menu (three dots) or select the service
   - Click Delete option

4. Confirm deletion
   - Confirm in the deletion dialog if one appears
   - Wait for deletion to complete

5. Verify service was deleted
   - Service no longer appears in the services list
   - Search/filter for service name returns no results

## Expected Result
- Service is removed from the services list
- Service cannot be found after deletion

## Context Updates
- Clear `created_service_id`
- Clear `created_service_name`
- Clear any other service-related context variables

## Notes
- This is the last test in the services subcategory
- Cleans up test data to leave system in clean state
