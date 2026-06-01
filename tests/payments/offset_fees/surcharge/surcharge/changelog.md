# Changelog: Surcharge

## 2026-06-01 - Initial migration
- Migrated from automation-js `features/salsa/offset-fees.feature` (scenario:
  Surcharge).
- API setup: paid $100 appointment service, client (+portal token), past
  appointment, credit-card + ACH enablement. UI setup: mock gateway, card on file.
- Test: enable surcharge (default 3%), pay via client-portal checkout, assert fee
  badge / summary / processing line / success ($103), verify Back Office payment.
