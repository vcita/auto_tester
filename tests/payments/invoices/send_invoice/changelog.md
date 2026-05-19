# Changelog

## 2026-05-19 - Harden Record Payment Dialog
**Phase**: Test
**Author**: Cursor AI
**Reason**: Stress runs intermittently timed out while opening or submitting the invoice record-payment dialog.
**Changes**:
- Added retry logic that re-queries the Take payment button and Record payment action.
- Searched both page and invoice iframe scopes for the menu item.
- Added a DOM-click fallback for Angular menu opening and force-clicked the final Record action.
