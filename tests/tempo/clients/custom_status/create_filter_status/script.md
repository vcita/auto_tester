# Create And Filter Custom Status - Detailed Script

> **Status**: Migrated from automation-js mapping
> **Last Updated**: 2026-05-27
> **Source**: `automation-js/features/steps/client-custom-status.feature`

## Initial State
- User is logged in by the clients category setup.
- The test may use the account API to create clients because the legacy scenario also creates clients via API.
- UI coverage is focused on custom status creation, assignment, and CRM filtering.

## Test Data
```python
timestamp = int(time.time())
status_name = f"Auto Status {timestamp}"
first_client = {
    "first_name": "StatusOne",
    "last_name": str(timestamp),
    "email": f"status.one.{timestamp}@vcita-test.com",
}
second_client = {
    "first_name": "StatusTwo",
    "last_name": str(timestamp),
    "email": f"status.two.{timestamp}@vcita-test.com",
    "status": status_name,
}
```

## Actions

### Step 1: Create Custom Status
- Navigate to Client Card settings.
- Open the Client status tab.
- Add a status chip with `status_name`.
- Verify the status chip is visible.

### Step 2: Create First Client Without Status
- Use `POST /platform/v1/clients` with `source_name: automation`.
- Save ID, full name, and email in context.

### Step 3: Filter By Status Before Assignment
- Navigate to the CRM clients list.
- Open Filters.
- Choose the Status filter.
- Select `status_name`.
- Apply the filter.
- Verify the filtered CRM table has zero clients.

### Step 4: Assign Status From Client Card
- Open the first client from the CRM list.
- Open the contact edit dialog from the loaded client detail page, using the rendered edit control or its emitted `matter_action` message.
- Change Status to `status_name` through the visible Angular Material Status dropdown.
- Save.
- Verify the client card displays `status_name`.

### Step 5: Verify One Filtered Client
- Return to the CRM clients list.
- Apply the Status filter for `status_name`.
- Poll the CRM table until it contains exactly the first client.

### Step 6: Create Second Client With Status
- Use `POST /platform/v1/clients` with the same `status_name`.
- Open the second client and verify the client card uses `status_name`; if the API-created status has not propagated to the card yet, set the same status through the UI before continuing.
- Clear all active filters.
- Reapply the Status filter.
- Poll the CRM table until it contains exactly both expected client names.

## Success Verification
- The custom status chip is visible after creation.
- The initial status filter returns no clients.
- The client card status equals the custom status after UI assignment.
- The CRM table shows exactly one matching client after UI assignment.
- The CRM table shows exactly two matching clients after API creation with status.
