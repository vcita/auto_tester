# Delete Note from Matter

## Objective
Delete a note from a matter to verify the note deletion functionality.

## Prerequisites
- User is logged in (handled by parent category _setup)
- Matter exists with a note (from edit_note test)
- `created_matter_id` is available in context
- `edited_note_content` is available in context (to identify the note to delete)

## Test Steps

1. **Navigate to Matter Detail Page**
   - Go to: `https://app.vcita.com/app/clients/{created_matter_id}`
   - Wait for page to load

2. **Find the Note to Delete**
   - Locate the note with content matching `edited_note_content`
   - Look for delete button/icon for that note

3. **Delete the Note**
   - Click delete button
   - Confirm deletion if prompted (handle confirmation dialog)

4. **Verify Note Was Deleted**
   - Confirm the note no longer appears in the notes section
   - Verify the notes list/count has decreased

## Context Cleanup
After successful deletion:
- Remove `created_note_content` from context
- Remove `edited_note_content` from context

## Expected Result
- Note is successfully deleted
- Note no longer appears in the matter's notes section
- Context is cleaned up for subsequent tests
