# Changelog

## 2026-05-19 - Stabilize Partial Payment Amount Entry
**Phase**: Test
**Author**: Cursor AI
**Reason**: Partial payment needed to work with standalone setup and full workflow invoice state.
**Changes**:
- Created an invoice prerequisite when none exists.
- Made billing navigation work from invoice pages, order lists, and expanded sidebar state.
- Reworked amount entry to clear, blur, validate the total, and preserve Cash selection.
- Updated the partial amount to stay below taxed invoice totals.
