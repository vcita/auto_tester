# Delete Service Function

## Objective

Delete a service by its name from the Services list. Used for test teardown to clean up test data.

## Parameters

- **name** (required): Name of the service to delete

## Prerequisites

- User is logged in
- Service with the given name exists
- User has permission to delete services

## Steps

1. Navigate to Settings from sidebar
2. Click on Services section
3. Find and click on the service by name in the list
4. Click the Delete button
5. Confirm deletion in the dialog
6. Verify service is removed from list

## Returns

Nothing - service is deleted from the system

## Success Criteria

- Service no longer appears in the services list
- Redirected back to Services list after deletion
