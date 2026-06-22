# Edit Event Changelog

## 2026-05-27 - Stabilized Required Location Field

**Phase**: test.py
**Author**: Cursor AI (stabilization)
**Reason**: Event edit opened the dialog and changed max attendance, but Save was blocked by a required "Where" field.

**Root Cause**: Editing the event can expose the location field as required even though the event was created with "My business address".

**Fix Applied**:
1. Fill the "Where" field when it is present before saving.
2. Keep the max-attendance update and final `12 Registered` verification.
3. Cap touched waits at 5000ms.

**Scope / Quality**: The edit assertion remains intact; the fix only satisfies a required form field so the existing save can complete.

---

## 2026-01-24 - Initial Build
**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration

**Changes**:
- Generated script.md from MCP exploration
- Generated test.py from script.md
- Modifies event details (max attendance) via Edit dialog
- Verifies changes are reflected in event view
