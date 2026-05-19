# Changelog

## 2026-05-19 - Stabilize Taxed Invoice Numbering
**Phase**: Test
**Author**: Cursor AI
**Reason**: The full payments workflow needed invoice numbering to create a valid taxed invoice without slow or unavailable invoice-details editing.
**Changes**:
- Removed unreliable invoice label and number editing from the dialog.
- Selected the API-created paid service from context instead of fallback custom items.
- Added sender billing address recovery and generated invoice-number verification.
- Verified invoice totals include the configured default tax.
