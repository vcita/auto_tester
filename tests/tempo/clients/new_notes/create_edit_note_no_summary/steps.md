# Create and Edit Note (No Summary)

## Objective
Verify the new POV notes flow: create a note from the client Notes tab, confirm it appears as a preview card with no AI chrome, then edit it and confirm the updated content is visible. Runs with `rollout.clients.new_notes` ON and `note_summary` OFF.

## Prerequisites
- Runs in the isolated `new_notes` subcategory. The subcategory `_setup` enables
  `rollout.clients.new_notes` **before login** (per-business flag read by the SPA at app load),
  logs in, and creates a client matter via API.
- Feature flag for AI note summary (`rollout.ai.note_summary`) is OFF (default — do not enable it)
- User is logged in and on the matter detail page (from `new_notes/_setup`)
- A client with at least one matter exists (`created_matter_id` in context from `_setup`)

## Steps

1. Navigate to the client matter page and click the Notes tab
   - Expected: The Notes tab is visible and loaded (showing the new-UI notes list, not the legacy dialog)

2. Click "Add note"
   - Expected: The new POV add-note popup opens, showing an optional title field and a rich-text body area

3. Type a note title ("Automation Note Title") and body text ("Automation note body"), then click Save
   - Expected: The popup closes and the Notes tab is visible; a note preview card appears in the list showing the title and body text just entered; no AI summary section, loading spinner, or AI chrome is visible on the card

4. Click the note card or open its 3-dot menu and choose Edit
   - Expected: The edit popup opens with the title and body content prefilled (matching what was entered in step 3)

5. Clear the body text and type new content ("Edited automation note body"), then click Save
   - Expected: The popup closes; the note preview card in the list reflects the new body content

## Context Updates
- `created_note_title`: `"Automation Note Title"` (for identifying the note in edit step)
- `created_note_body`: `"Automation note body"` (original body)
- `edited_note_body`: `"Edited automation note body"` (for verifying the edit)

## Expected Result
- A note is created via the new POV popup and immediately visible as a preview card in the list
- The card shows title and body content with no AI summary or AI chrome (note_summary is OFF)
- Editing the note via the edit popup updates the card content immediately
