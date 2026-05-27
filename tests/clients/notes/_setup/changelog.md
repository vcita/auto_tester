# Changelog - Notes Setup

## 2026-05-26 - Independent Subcategory Setup

**Issue**: `clients/notes` could not be stress-tested independently because it expected `created_matter_id` from the full `clients/create_matter` UI flow.

**Fix Applied**:
- Added a notes-local setup that creates the required matter via API.
- Navigates directly to the created matter detail page with a 5000ms navigation timeout.
- Preserves the note tests' UI coverage by only replacing the prerequisite setup path.

## 2026-05-27 - Preserve Full Clients Matter

**Issue**: The notes setup also ran inside full `clients` category stress tests and overwrote the UI-created `created_matter_id`, causing the later `delete_matter` test to delete the notes API matter instead.

**Fix Applied**:
- Reuse an existing `created_matter_id` when full clients sequencing already created one.
- Create an API matter only for isolated `clients/notes` runs.
- Save isolated setup ownership under `notes_setup_matter_*` so teardown can clean up only that path.
