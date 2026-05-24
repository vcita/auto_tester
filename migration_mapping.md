# automation-js to auto_tester Migration Mapping

## PoC Source

- Legacy feature: `automation-js/features/steps/client-custom-status.feature`
- Legacy steps: `automation-js/steps/desktop/clients.js`
- Legacy page objects:
  - `pages/desktop/Frontage/Clients/clientCardSettings.js`
  - `pages/desktop/Frontage/Clients/newClients.js`
  - `pages/desktop/Frontage/Clients/client.js`
- auto_tester target: `tests/clients/custom_status`

## Original Scope

### Scenario: create

1. Create a custom client status.
2. Create a client without that status via API.
3. Apply the CRM Status filter and verify the client list is empty.
4. Open the current client and set the custom status.
5. Verify the current client card shows that status.
6. Reapply the CRM Status filter and verify the first client appears.
7. Create a second client via API with the custom status.
8. Clear and reapply the CRM Status filter.
9. Verify both clients appear in the filtered CRM table.

### Scenario: delete

1. Create a custom client status.
2. Create a client with that status via API.
3. Attempt to delete the status and verify deletion is blocked.
4. Reassign the current client to `Lead`.
5. Verify the current client card shows `Lead`.
6. Delete the now-unused custom status and verify the status no longer exists.

## Legacy Behavior Details

- `user creates custom status` opens Client Card settings, selects the `Client status` tab, adds a chip, and waits for a success toast.
- `user deletes custom status` removes the status chip. When the status is in use, the confirmation dialog is dismissed and the status must remain available.
- `user creates new client via API` calls `POST /platform/v1/clients` with `source_name: automation`; optional `status` is passed directly.
- `user sets status ... to current client` opens the client detail page, edits contact info, chooses the Status dropdown value, and saves.
- `current client status is ...` reads `.contact-status-value` from the client card and polls until the expected value appears.
- `user adds "Status" filter with value ...` opens CRM filters, chooses the status filter, selects the status value, and applies it.
- `search crm filtered clients` polls the CRM table because the backing index can lag API-created clients.

## auto_tester Translation

- Place the migration under `tests/clients/custom_status` because the behavior belongs to CRM/client profile management.
- Keep it as a subcategory so the PoC can run independently from the existing create/edit/delete matter sequence.
- Use API setup only for client creation, matching the legacy scenario and keeping UI coverage focused on custom status behavior.
- Use generated unique status names and client emails to avoid collisions across repeated runs.
- Preserve all original assertions:
  - Filter has no results before assignment.
  - Client card status changes to the custom status.
  - Filter shows exactly one matching client after UI assignment.
  - Filter shows both matching clients after API-created client with status.
  - In-use status deletion is blocked.
  - Reassigning to `Lead` updates the client card.
  - Unused custom status can be deleted and disappears from available status filters.

## Implementation Files

- `tests/clients/custom_status/_category.yaml`
- `tests/clients/custom_status/create_filter_status/steps.md`
- `tests/clients/custom_status/create_filter_status/script.md`
- `tests/clients/custom_status/create_filter_status/test.py`
- `tests/clients/custom_status/create_filter_status/changelog.md`
- `tests/clients/custom_status/delete_status/steps.md`
- `tests/clients/custom_status/delete_status/script.md`
- `tests/clients/custom_status/delete_status/test.py`
- `tests/clients/custom_status/delete_status/changelog.md`

## DoD Checkpoint

Before extracting a reusable migration skill:

- Compile every new Python file.
- Run discovery for `clients`.
- Run the focused `clients/custom_status` category.
- Run a focused stability pass when the environment supports it.
- Confirm zero scope loss against this mapping.
