# Create Service

## Objective
Create a new 1-on-1 service (appointment type) with name, duration, and price to verify service creation functionality.

## Prerequisites
- User is logged in (from category _setup)
- User has permission to manage services

## Test Data
- Service name: "Test Consultation {timestamp}"
- Duration: 30 minutes
- Price: $50

## Steps

1. Navigate to Settings > Services
   - Click Settings in sidebar or header menu
   - Click Services in settings menu

2. Click "Add Service" or "+" button
   - Wait for service creation form/dialog to appear

3. Fill in service details
   - Enter service name: "Test Consultation {timestamp}"
   - Set duration: 30 minutes
   - Set price: $50
   - Leave other fields as default

4. Save the service
   - Click Save button
   - Wait for confirmation/success message

5. Verify service was created
   - Service appears in the services list
   - Service name, duration, and price are correct

## Expected Result
- New service is created and visible in services list
- Service has correct name, duration, and price

## Context Updates
- Save `created_service_id` for subsequent tests
- Save `created_service_name` for verification

## Notes
- Service name includes timestamp for uniqueness
- This service will be used by edit_service and delete_service tests
