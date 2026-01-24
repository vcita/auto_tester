# Create Client Function

## Objective

Create a minimal client (matter/property) for test setup purposes. This is a simplified version intended for test setup - it creates a client with only required fields.

## Parameters

- **first_name** (optional): First name of the client (defaults to "Test")
- **last_name** (optional): Last name (defaults to "Client{timestamp}")
- **email** (optional): Email address (defaults to generated test email)

## Prerequisites

- User is logged in

## Steps

1. Navigate to Dashboard
2. Click "Add property" in Quick actions panel
3. Wait for the client form to load in iframe
4. Fill First Name (required)
5. Fill Last Name
6. Fill Email
7. Click Save
8. Verify client is created (URL changes to client page)
9. Extract client ID from URL

## Returns

- **created_client_id**: ID of the created client
- **created_client_name**: Full name of the client (first + last)
- **created_client_email**: Email of the client

## Success Criteria

- Client page opens after save
- Client ID is captured from URL
