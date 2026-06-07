# Changelog: Paying for appointment

## 2026-06-06 - Initial migration (VCITA2-13857)

- Migrated from `automation-js/features/salsa/appointment-payments.feature`
  scenario 3 "paying for appointment" (@gate).
- Setup denies point_of_sale so take payment uses the legacy record dialog.
- Records $10 (DUE $90.00 of $100.00, 1 payment) then $90 (PAID $100.00, 2
  payments), via the appointment detail page payment-status card.
