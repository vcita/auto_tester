# Edit Matter Test

## Objective

Edit an existing matter (property) by modifying 2-3 fields and verify the changes are saved correctly.

## Prerequisites

- Must run after `create_matter` test
- Requires context data:
  - `created_matter_id`: The ID of the matter to edit
  - `created_matter_name`: The name for verification

## Fields to Modify

1. **Help Request** ("How can we help you?") - Text field
2. **Special Instructions** - Text field  
3. **Private Notes** - Text field

These fields were chosen because:
- They are text fields (easy to verify changes)
- They don't affect other test functionality (delete still works)
- They are visible on the matter detail page

## Expected Flow

### Part 1: Navigate to Matter

1. The test starts on the matter detail page (from create_matter)
2. OR navigate to matter using the ID from context: `/app/clients/{matter_id}`

### Part 2: Open Edit Form

1. Find and click the edit button/pencil icon on the matter detail page
2. Wait for edit form/modal to appear

### Part 3: Modify Fields

1. Clear and fill "How can we help you?" with new value
2. Clear and fill "Special instructions" with new value
3. Clear and fill "Private notes" with new value

### Part 4: Save Changes

1. Click Save button
2. Wait for save to complete

### Part 5: Verify Changes (User Perspective)

1. Check that the new values are visible on the matter detail page
2. This is what a real user would do to confirm their edit worked

## Test Data

Generate new values with timestamp to ensure uniqueness:
- help_request: "EDITED: Need updated lawn service - {timestamp}"
- special_instructions: "EDITED: New gate code is 9999 - {timestamp}"
- private_notes: "EDITED: Customer updated preferences - {timestamp}"

## Context Updates

After successful edit, update context:
- `edited_help_request`: The new help request value
- `edited_special_instructions`: The new special instructions value
- `edited_private_notes`: The new private notes value

## Success Criteria

- Edit form opens successfully
- All 3 fields are modified
- Save completes without error
- New values are visible on the matter detail page after save
