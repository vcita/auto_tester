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

## 2026-06-07 - Restore exact credit-refund caption (scope)

- The legacy `package_credit_refunded` check asserts the full caption
  `1 credit refund from {package} package was issued on {Mon DD}`
  (meetingHelper). The migration previously only checked the substring
  "credit refund" + package name; `_assert_package_details` now verifies the
  complete phrasing **including the issue date** (date format mirrors the legacy
  `Intl.DateTimeFormat('en-US', {month:'short', day:'2-digit'})`, accepting
  today ±1 day to absorb any account/runner timezone offset).
- `redeem_with_package=false` for meeting1 is preserved as a behavior assertion
  (meeting1 completes to DUE $100, i.e. not auto-redeemed) rather than a UI
  checkbox: API scheduling never auto-redeems and the package is assigned after
  scheduling, so the legacy redeem=false outcome holds.
