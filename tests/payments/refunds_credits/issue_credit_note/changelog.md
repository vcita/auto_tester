# Changelog

## 2026-05-19 - Handle Unsupported Credit Notes
**Phase**: Test
**Author**: Cursor AI
**Reason**: Credit note action is not always available and the old Edit-menu locator timed out.
**Changes**:
- Opened the top invoice overflow menu instead of assuming an Edit menu exists.
- Marked credit notes as not supported when no credit action appears.
- Made invoice navigation work from both standalone and full workflow states.
