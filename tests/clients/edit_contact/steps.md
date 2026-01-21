# Edit Contact Information

> **Type**: Test
> **Status**: Draft
> **Last Updated**: 2026-01-21
> **Note**: This test edits CONTACT fields (name, address, etc.) - distinct from edit_matter which edits PROPERTY fields

## Objective

Edit the contact information fields of an existing matter and verify the changes are saved correctly. This demonstrates the ability to modify contact-level data separately from property/matter data.

## Prerequisites

- Must run after `create_matter` and `edit_matter` tests
- Requires context data:
  - `created_matter_id`: The ID of the matter to edit
  - `created_matter_name`: The current name (for navigation/verification)

## Fields to Modify

1. **Last Name** - Text field, affects the display name
2. **Address** - Text field, visible in contact information section
3. **Referred by** - Text field, visible after expanding contact info

These fields were chosen because:
- They are distinct from the property fields edited in `edit_matter`
- They are text fields (easy to clear and fill)
- Changes are verifiable in the UI
- They don't break other test functionality

**Note**: We avoid editing First Name to minimize context update complexity. If Last Name is edited, we'll update `created_matter_name` in context.

## Expected Flow

### Part 1: Navigate to Matter Detail Page

1. Verify we have `created_matter_id` from context
2. Navigate to matter detail page if not already there: `/app/clients/{matter_id}`
3. Wait for page to load and verify correct matter

### Part 2: Open Edit Contact Dialog

1. Find the contact information section on the matter detail page
2. Click the edit button for contact information (distinct from "Edit property info")
3. Wait for the edit contact dialog/form to appear

### Part 3: Modify Contact Fields

1. Find and clear the "Last Name" field
2. Fill new Last Name value with timestamp
3. Find and clear the "Address" field  
4. Fill new Address value
5. Find and clear the "Referred by" field (may need to expand "Show more")
6. Fill new Referred by value

### Part 4: Save Changes

1. Click the Save button
2. Wait for dialog to close
3. Wait for page to update

### Part 5: Verify Changes (User Perspective)

1. Re-open the edit contact dialog
2. Verify Last Name field has the new value
3. Verify Address field has the new value
4. Verify Referred by field has the new value
5. Close the dialog

## Test Data

Generate new values with timestamp to ensure uniqueness:
- last_name: "ContactEdit{timestamp}"
- address: "EDITED: {random number} Updated Street, New City"
- referred_by: "EDITED: Test Referral Source - {timestamp}"

## Context Operations

**Reads from context:**
- `created_matter_id`: ID of the matter to edit
- `created_matter_name`: Current full name (First + Last)

**Saves to context:**
- `edited_last_name`: The new last name value
- `edited_address`: The new address value  
- `edited_referred_by`: The new referred by value
- `created_matter_name`: Updated to reflect new last name (First + new Last)

## Success Criteria

- Edit contact dialog opens successfully
- All 3 contact fields are modified
- Save completes without error
- New values are visible when re-opening the edit dialog
- Context is updated with new values

## Notes

- The contact edit is separate from property/matter edit
- Look for edit button in the "Contact information" section, not the property card
- May need to click "Show more" to see the Referred by field
- The form is likely inside an iframe (same as create/edit matter forms)
