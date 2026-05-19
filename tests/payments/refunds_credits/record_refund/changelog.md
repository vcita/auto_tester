# Changelog

## 2026-05-19 - Add Paid Invoice Prerequisite
**Phase**: Test
**Author**: Cursor AI
**Reason**: Refunds and Credits had no invoice to refund when run standalone.
**Changes**:
- Created and paid an invoice prerequisite when no invoice exists.
- Reused the current invoice during full category workflow runs.
- Removed brittle checkout navigation from the invoice-opening path.
