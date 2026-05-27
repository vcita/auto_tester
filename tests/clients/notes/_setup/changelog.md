# Changelog - Notes Setup

## 2026-05-26 - Independent Subcategory Setup

**Issue**: `clients/notes` could not be stress-tested independently because it expected `created_matter_id` from the full `clients/create_matter` UI flow.

**Fix Applied**:
- Added a notes-local setup that creates the required matter via API.
- Navigates directly to the created matter detail page with a 5000ms navigation timeout.
- Preserves the note tests' UI coverage by only replacing the prerequisite setup path.
