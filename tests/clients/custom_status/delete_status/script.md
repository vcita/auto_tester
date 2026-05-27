# Delete Custom Status - Detailed Script

> **Status**: Migrated from automation-js mapping
> **Last Updated**: 2026-05-27
> **Source**: `automation-js/features/steps/client-custom-status.feature`

## Initial State
- User is logged in by the clients category setup.
- This test uses its own unique status so it is independent from the filter scenario.

## Test Data
```python
timestamp = int(time.time())
status_name = f"Delete Status {timestamp}"
client = {
    "first_name": "StatusDelete",
    "last_name": str(timestamp),
    "email": f"status.delete.{timestamp}@vcita-test.com",
    "status": status_name,
}
```

## Actions

### Step 1: Create Custom Status
- Navigate to Client Card settings.
- Open the Client status tab.
- Add a status chip with `status_name`.
- Verify the status chip is visible.

### Step 2: Create Client With Status
- Use `POST /platform/v1/clients` with `status: status_name`.
- Save ID, full name, and email in context.

### Step 3: Verify In-Use Status Cannot Be Deleted
- Open Client Card settings.
- Remove the custom status chip.
- Verify a confirmation or blocking dialog appears.
- Dismiss the dialog.
- Verify the status chip remains visible in Client Card settings.

### Step 4: Reassign Client To Lead
- Open the API-created client from the CRM list.
- Open the contact edit dialog from the loaded client detail page, using the rendered edit control or its emitted `matter_action` message.
- Change Status to `Lead` through the visible Angular Material Status dropdown.
- Save.
- Verify the client card displays `Lead`.

### Step 5: Delete Unused Status
- Return to Client Card settings.
- Remove the custom status chip.
- Accept the delete confirmation when shown.
- Verify the status chip no longer appears in Client Card settings.

## Success Verification
- In-use status deletion is blocked.
- The client can be reassigned to `Lead`.
- The unused status is deleted.
- The deleted status is removed from Client Card settings.
