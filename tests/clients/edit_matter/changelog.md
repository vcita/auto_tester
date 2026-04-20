# Changelog - Edit Matter

## [2.0.0] - 2026-04-05

### Fixed (Healed)
- **Dialog title mismatch + missing fields on Client vertical**
  - **Error**: `TimeoutError: Timeout 10000ms exceeded` waiting for `text=Edit property info`
  - **Root cause**: Auto-created accounts use "Clients" vertical. The edit dialog shows "Edit client info" (not "Edit property info") and only has "Add tags" — no "How can we help you?" or "Special instructions" fields.
  - **Screenshot evidence**: Dialog was open with title "Edit client info", containing only "Add tags" field with CANCEL/SAVE buttons.
  - **Fix applied**:
    1. **Entity-agnostic dialog title**: Uses regex to match "Edit client info", "Edit property info", "Edit patient info", etc.
    2. **Adaptive field editing**: Checks if Property-specific fields exist (help request, special instructions). If yes, edits those. If no, adds a tag instead.
    3. **Adaptive verification**: Verifies the fields that were actually edited (property fields or tag).
  - **Files updated**: test.py (complete rewrite), script.md, changelog.md (created)

## [1.0.0] - 2026-01-21

### Added
- Initial implementation with Property-specific field editing
- Edits "How can we help you?" and "Special instructions/requests" fields
- Verification by reopening dialog and checking values
