# Notes Setup - Detailed Script

## Objective
Open the matter required by add, edit, and delete note tests without changing full-category cleanup ownership.

## Initial State
- Parent Clients setup has logged in.
- The runner has injected auto-account and API configuration into context.

## Actions

### Step 1: Resolve Matter
- **Action**: Reuse `created_matter_id` when present.
- **Full clients behavior**: Use the matter created by `clients/create_matter`.

### Step 2: Create Matter Via API For Isolated Runs
- **Action**: Call helper only when `created_matter_id` is absent.
- **Function**: `create_note_matter_via_api`
- **Expected return**: created matter details
- **Context**: Also save `notes_setup_matter_id` for teardown.

### Step 3: Navigate To Matter Page
- **Action**: Open direct client detail URL
- **Target**: `/app/clients/{created_matter_id}`
- **Wait for**: URL contains `/app/clients/`
- **Timeout**: 5000ms

## Success Verification
- Created matter ID exists in context.
- Browser URL contains the created matter ID.
- Full-category runs do not replace the original `created_matter_id`.
