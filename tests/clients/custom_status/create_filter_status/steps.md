# Create And Filter Custom Status

## Objective
Verify that a custom client status can be created, assigned to clients, and used as a CRM table filter.

## Prerequisites
- User is logged in from the clients category setup.
- A fresh auto-created account is available for the run.

## Steps
1. Create a new custom client status in Client Card settings.
2. Create a client without the custom status.
3. Filter the CRM table by the custom status.
4. Verify the filtered CRM table has no clients.
5. Open the created client and assign the custom status.
6. Verify the client card shows the custom status.
7. Filter the CRM table by the custom status again.
8. Verify only the assigned client appears.
9. Create a second client with the custom status.
10. Verify the second client card shows the custom status.
11. Clear and reapply the custom status filter.
12. Verify both matching clients appear in the filtered CRM table.

## Expected Result
- The custom status is available in client status controls.
- The custom status filter initially returns no clients.
- The first client appears after the status is assigned from the UI.
- Both clients appear after a second client is created with that status.

## Context Updates
- Save `custom_status_filter_name`.
- Save `custom_status_first_client_id`, `custom_status_first_client_name`, and `custom_status_first_client_email`.
- Save `custom_status_second_client_id`, `custom_status_second_client_name`, and `custom_status_second_client_email`.
