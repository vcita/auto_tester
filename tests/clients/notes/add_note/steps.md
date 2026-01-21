# Add Note to Matter

## Objective
Add a note to an existing matter to verify the note creation functionality.

## Prerequisites
- User is logged in (handled by parent category _setup)
- Matter exists (created by create_matter test in parent category)
- `created_matter_id` is available in context
- `created_matter_name` is available in context

## Test Steps

1. **Navigate to Matter Detail Page**
   - Go to: `https://app.vcita.com/app/clients/{created_matter_id}`
   - Wait for page to load

2. **Open Add Note Dialog**
   - Look for "Add note" button or similar action
   - Click to open the note creation dialog/form

3. **Enter Note Content**
   - Fill in the note text field with test content
   - Note content should include a timestamp for uniqueness

4. **Save the Note**
   - Click the save/submit button
   - Wait for confirmation

5. **Verify Note Was Created**
   - Confirm the note appears in the matter's notes section
   - Verify the note content matches what was entered

## Test Data
```python
test_data = {
    "note_content": f"Test note created at {timestamp} - This is an automated test note.",
}
```

## Context Updates
After successful note creation:
- `created_note_content` - The note text that was created (for edit_note test)

## Expected Result
- Note is successfully added to the matter
- Note content is visible in the notes section
- Context is updated with note information for subsequent tests
