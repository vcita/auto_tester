# Changelog: Convenience Fee Flat

## 2026-06-01 - Initial migration
- Migrated from automation-js `features/salsa/offset-fees.feature` (scenario:
  Convenience fee - flat fee).
- API setup: paid $100 appointment service, client (+portal token), past
  appointment, credit-card + ACH enablement. UI setup: mock gateway, card on file.
- Test: enable $1 flat convenience fee, pay via client-portal checkout, assert fee
  badge / summary / processing line / success ($101), verify Back Office payment.
