# Changelog: Schedule appointment with packaged service

## 2026-06-06 - Initial migration (VCITA2-13857)

- Migrated from `automation-js/features/salsa/appointment-payments.feature`
  scenario 6 "Schedule appointment with packaged service".
- Completes meeting1 (DUE $100), redeems meeting2 with the package
  (PAID $0, redeemed_with_package), then cancels meeting2's redemption
  (DUE $100, package_credit_refunded).
- Appointments are seeded for *earlier today* (lead_days=0) so the "display a
  fee" request is DUE (due today) after completion; future-dated stays NOT YET
  DUE and a past date becomes OVERDUE. `mark_appt_completed` tolerates an
  already-completed (auto-completed) appointment.
- Deviation (documented): legacy scheduled both appointments via the
  QuickActions UI to choose the redeem-with-package option at scheduling; here
  the appointments are API-seeded and redemption is driven through the
  appointment-page redeem-package / cancel-redemption buttons (same package
  UI as the event redeem scenario). The UI scheduling dialog is an out-of-scope
  prerequisite; all three payment-request states are preserved.
