# Changelog

## 2026-05-19 - Support Taxed Workflow Totals
**Phase**: Test
**Author**: Cursor AI
**Reason**: Edit Invoice passed standalone but failed in the full payments workflow after tax settings made the service taxable.
**Changes**:
- Calculated the expected added service amount with configured tax when present.
- Removed the dropdown y-position filter that hid valid service options.
- Force-clicked the visible service option to handle overlay and animation timing.
