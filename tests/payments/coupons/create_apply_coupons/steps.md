# Create and Apply Coupons — Steps

Migrated from `automation-js/features/salsa/coupons.feature`
(scenario: *Create and apply coupons of types fixed & percentage*).

Precondition (from setup): three paid $100 appointments exist (`appointment_1/2/3`),
each with a `NOT YET DUE` payment request.

1. Open the Coupons settings page.
2. Create three coupons:
   - `20 off coupon` — Fixed amount, 20
   - `10% coupon` — Percentage, 10
   - `100% coupon` — Percentage, 100
3. Verify the coupons list shows the discounts: `20 off coupon → $20 off`, `10% coupon → 10% off`, `100% coupon → 100% off`.
4. Apply each coupon to its appointment and verify the resulting payment request:
   - `20 off coupon` → `appointment_1` → `NOT YET DUE`, `$80.00`
   - `10% coupon` → `appointment_2` → `NOT YET DUE`, `$90.00`
   - `100% coupon` → `appointment_3` → `PAID`, `$0.00`
