# Delete Custom Status

## Objective
Verify that an in-use custom client status cannot be deleted, and that the same status can be deleted after clients stop using it.

## Prerequisites
- User is logged in from the clients category setup.
- A fresh auto-created account is available for the run.

## Steps
1. Create a new custom client status for deletion validation.
2. Create a client with that custom status.
3. Attempt to delete the in-use custom status.
4. Verify deletion is blocked and the status remains available.
5. Open the client and change its status to `Lead`.
6. Verify the client card shows `Lead`.
7. Delete the now-unused custom status.
8. Verify the custom status is no longer available in status filters.

## Expected Result
- Deleting an in-use status is blocked.
- Reassigning the client to `Lead` removes the status usage.
- The unused custom status can be deleted.
- The deleted status no longer appears as a CRM Status filter option.

## Context Updates
- Save `custom_status_delete_name`.
- Save `custom_status_delete_client_id`, `custom_status_delete_client_name`, and `custom_status_delete_client_email`.
- Clear delete-flow context values after successful cleanup.
