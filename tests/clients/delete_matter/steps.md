# Delete Matter

> **Type**: Test
> **Status**: Pending exploration
> **Last Updated**: 2026-01-21
> **Knowledge Source**: https://support.vcita.com/hc/en-us/articles/360040922094-Add-Clients-and-Contacts-in-vcita
> **Note**: "Matter" is vcita's general entity - called "Property" for Home Services, "Patient" for Healthcare, etc.

## Objective
Verify that a user can delete an existing matter from the Clients list, and confirm the deletion is permanent.

## Prerequisites
- User must be logged in (Call: login function)
- A matter must exist to delete (uses `created_matter_name` and `created_matter_id` from context, set by create_matter test)
- User should be on the dashboard

## Steps

### Part 1: Navigate to Clients List
1. Click "Clients" in the left sidebar navigation
2. Wait for the clients list to load

### Part 2: Find and Select the Matter
3. Search for the matter by name in the list search box (so it appears on the first page; list is paginated)
4. Locate the matter to delete by name (from context: `created_matter_name`)
5. Check the checkbox next to the matter's name to select it

### Part 3: Delete the Matter
6. Click the "More" button (dropdown menu with additional actions)
7. Click "Delete" from the dropdown menu options
8. Click "Delete" again in the confirmation dialog to confirm deletion

### Part 4: Verify Deletion
9. Verify the matter is no longer visible in the clients list
10. Optionally search for the matter name to confirm it doesn't exist

## Expected Result
- Matter is successfully deleted
- Matter no longer appears in the clients list
- Confirmation message may be displayed
- Searching for the deleted matter returns no results

## Test Data
Uses data from context (set by create_matter test):
- `created_matter_name`: The full name of the matter to delete
- `created_matter_id`: The ID of the matter (for URL verification if needed)
- `created_matter_email`: The email of the matter (for search verification)

## Context Operations
Reads from context:
- `created_matter_name`: Name to search for in the clients list
- `created_matter_id`: ID for additional verification

Clears from context after successful deletion:
- `created_matter_name`
- `created_matter_email`
- `created_matter_id`

## Notes
- This test depends on create_matter test running first to create a matter
- The delete operation requires selecting the matter via checkbox, not clicking on it
- The "More" button appears after selecting at least one matter
- A confirmation dialog appears to prevent accidental deletions
- Deletion is permanent and cannot be undone
