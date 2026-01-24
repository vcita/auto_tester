# Create Service Function

## Objective

Create a minimal 1-on-1 service that can be used for booking appointments. This is a simplified version intended for test setup - it creates a service with default settings.

## Parameters

- **name** (required): Name of the service to create (should include timestamp for uniqueness)

## Prerequisites

- User is logged in
- User has access to Settings > Services

## Steps

1. Navigate to Settings from sidebar
2. Click on Services section
3. Click "New service" dropdown button
4. Select "1 on 1 appointment" from dropdown menu
5. Enter service name in the "Service name" field
6. Select "Face to face" as location (simplest option)
7. Keep default duration (1 hour)
8. Keep "Free" pricing (default, simpler)
9. Click "Create" button
10. Wait for dialog to close and service to be created
11. Extract service ID from URL or list

## Returns

- **created_service_id**: The ID of the newly created service
- **created_service_name**: The name of the service (for verification)

## Success Criteria

- Service appears in the services list
- Service ID is captured and saved to context
