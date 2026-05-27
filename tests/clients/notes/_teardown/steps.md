# Notes Teardown

## Objective
Clean up the API-created matter used only when `clients/notes` runs as an isolated subcategory.

## Steps
1. Check whether `notes_setup_matter_id` exists in context.
2. If present, delete that matter through the API.
3. Clear the isolated notes setup context keys.

## Expected Result
- Isolated `clients/notes` runs leave no API-created matter behind.
- Full `clients` runs keep the original `created_matter_id` for the later `delete_matter` test.
