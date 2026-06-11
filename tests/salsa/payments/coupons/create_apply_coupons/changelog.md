# Changelog — create_apply_coupons

## 2026-05-31 — Initial migration (VCITA2-13736)

- Migrated `automation-js/features/salsa/coupons.feature` (scenario: *Create and apply coupons of types fixed & percentage*) into `tests/payments/coupons`.
- Created isolated-account subcategory with API-provisioned setup (3 paid $100 appointment services, 1 client, 3 future appointments) in `_setup`.
- Implemented `coupons_api.py` (paid service / client / appointment creation) and `coupons_helpers.py` (coupon create, list assertion, apply-to-appointment, payment-request assertion) against the Angular frontage iframe.
- Test creates a Fixed ($20) and two Percentage (10%, 100%) coupons via UI, verifies the discounts in the list, applies each to an appointment, and asserts the resulting payment requests ($80.00 / $90.00 NOT YET DUE, $0.00 PAID).
- Replaced legacy fixed sleeps with condition waits (capped at 5s); coupon-save confirmed via the share dialog, list verified by polling, payment-request verified via reactive status/balance assertions.

## 2026-06-01 — Wait/duration optimization (VCITA2-13736)

- Profiled per-phase timing and removed two wasted waits, cutting full-category runtime ~21% (70.5s → 55.8s):
  - `apply_coupon`: dropped the best-effort success-toast wait, which was always hitting its full 5s timeout (the `md-toast` selector never matched inside the iframe). The save dialog closing now signals completion and `assert_payment_request` already polls reactively for the updated balance — saving ~15s across the 3 applies (test step 41.8s → 30.2s).
  - `_setup` bookings: the 3 scheduling POSTs were the slowest setup phase (~4.7s each, serial). Issue the first sequentially (it creates the client's conversation record) then the remaining two in parallel — concurrent bookings for a brand-new client race on that creation (server 422 `message_count for nil`), so only the tail is parallelized (setup 28.7s → 25.5s).
- Re-validated: focused run green + 10/10 stress on integration.
