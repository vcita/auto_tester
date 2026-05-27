# Notes Setup - Detailed Script

## Objective
Create the matter required by add, edit, and delete note tests without depending on the full `clients/create_matter` UI flow.

## Initial State
- Parent Clients setup has logged in.
- The runner has injected auto-account and API configuration into context.

## Actions

### Step 1: Create Matter Via API
- **Action**: Call helper
- **Function**: `create_note_matter_via_api`
- **Expected return**: created matter details

### Step 2: Navigate To Matter Page
- **Action**: Open direct client detail URL
- **Target**: `/app/clients/{created_matter_id}`
- **Wait for**: URL contains `/app/clients/`
- **Timeout**: 5000ms

## Success Verification
- Created matter ID exists in context.
- Browser URL contains the created matter ID.
