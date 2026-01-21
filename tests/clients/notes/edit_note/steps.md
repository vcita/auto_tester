# Edit Note on Matter

## Objective
Edit an existing note on a matter to verify the note editing functionality.

## Prerequisites
- User is logged in (handled by parent category _setup)
- Matter exists with a note (created by add_note test)
- `created_matter_id` is available in context
- `created_note_content` is available in context (to identify the note)

## Test Steps

1. **Navigate to Matter Detail Page**
   - Go to: `https://app.vcita.com/app/clients/{created_matter_id}`
   - Wait for page to load

2. **Find the Note to Edit**
   - Locate the note with content matching `created_note_content`
   - Click edit button/icon for that note

3. **Modify Note Content**
   - Clear existing content
   - Enter new note content with "EDITED:" prefix and timestamp

4. **Save Changes**
   - Click save/update button
   - Wait for confirmation

5. **Verify Changes Were Saved**
   - Confirm the note now shows the updated content
   - Verify "EDITED:" prefix is visible

## Test Data
```python
test_data = {
    "new_note_content": f"EDITED: Updated note at {timestamp} - This note has been modified.",
}
```

## Context Updates
After successful edit:
- `edited_note_content` - The new note text (for verification in delete_note)

## Expected Result
- Note content is successfully updated
- Updated content is visible in the notes section
