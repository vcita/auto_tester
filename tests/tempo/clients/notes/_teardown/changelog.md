# Changelog - Notes Teardown

## 2026-05-27

### Added
- Added isolated notes cleanup that deletes only the matter created by `clients/notes/_setup`.

### Reason
- `clients/notes` can run both independently and inside the full `clients` category.
- Independent runs need cleanup for the API-created matter, while full-category runs must preserve the UI-created matter for `delete_matter`.
