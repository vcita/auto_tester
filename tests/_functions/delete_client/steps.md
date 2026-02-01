# Delete Client Function

## Objective

Delete a client (matter/property) by navigating to their detail page and using the delete option. Used for test teardown to clean up test data.

## Parameters

- **name** (optional): Name of the client to delete (defaults to context value `created_client_name`)
- **id** (optional): ID of the client to delete (defaults to context value `created_client_id`)

## Prerequisites

- User is logged in
- Client with the given name/id exists
- User has permission to delete clients

## Steps

1. Navigate to the Properties (clients) list page
2. Search for the client by name
3. Click on the client to open detail page
4. Click the "More" dropdown button
5. Select "Delete property" from the dropdown
6. Confirm deletion in the dialog by clicking "Delete" (approve popup)
7. Verify redirected back to Properties list
8. Clear context variables

## Returns

Nothing - client is deleted from the system

## Success Criteria

- Client no longer appears in search results
- Redirected to Properties list after deletion
- Context variables cleared
