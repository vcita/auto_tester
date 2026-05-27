# Notes Teardown - Detailed Script

## Objective
Delete only the matter created by the notes isolated setup path.

## Initial State
- Notes tests completed.
- `notes_setup_matter_id` may exist when the subcategory ran independently.

## Actions

### Step 1: Delete Isolated Notes Matter
- **Action**: Call helper
- **Function**: `delete_note_matter_via_api`
- **Behavior**: No-op when `notes_setup_matter_id` is absent.

## Success Verification
- Isolated notes matter context keys are cleared.
- Full-category `created_matter_id` is not deleted by notes teardown.
