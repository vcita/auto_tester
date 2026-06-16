# Changelog: take_with_tips (BO tips)

## 2026-06-07 - Migrate tips.feature scenario 1 (VCITA2-13899)

- Migrated from `automation-js/features/salsa/tips.feature` scenario "edit tips
  options & take payment with tips" into `tests/payments/tips_checkout/bo_payment_tips`.
- Setup (API): deny point_of_sale; enable tips flags; assign tips app; set tip
  options 55,66,77 + enable_tips_for_bo; client + suggest-to-pay $100 service +
  specific package ($150, assigned) + past appointment.
- Tips settings persisted via `POST /platform/v1/payment/settings`
  (`payment_settings.{tips, enable_tips_for_bo}`) with GET read-back - the legacy
  `PUT /v2/settings` is known to drop the tips field on the current backend.
- Test (UI): close-balance with ACH + 55% tip (asserts Multi-item $387.50, tip
  $137.50), then Quick Actions record custom item $5 with Custom $4.50 tip.
- New helpers: `tips_checkout_api` (assign_app, set_tips, dates, invoice/payment
  seeds) and `tips_checkout_bo` (close_client_balance, record_custom_payment_with_tip,
  add_followup_tip, assert_payment_page_with_tip). Reuses deposits_invoice_ui
  (Quick Actions record) and event_payments_helpers (Payments Received).
- Tip picker (`md-select[name='tip_option']` / `input[name='tip_amount']`) and tip
  row (`.tip-row .invoice-right-side`) have no product data-qa; legacy selectors
  reused and documented (suggest adding data-qa).
- CRITICAL ordering: the Angular close-balance controller computes `showTips` from
  `Account.settings.{enable_tips_for_bo, tips}`, which is loaded at login. All API
  seeding (tips settings + app assign) must run BEFORE `fn_login` so the first page
  load sees tips - otherwise the tip picker never renders. Setup logs in last.
- `assign_app` requires Admin auth (`POST /platform/v1/apps/tips/assign` returns 401
  with the account Bearer token); switched to admin_headers().
- Stability: the confirm button flips to `aria-disabled="true"` while submitting, so
  keying the confirm locator on `[aria-disabled="false"]` and waiting on the button to
  hide was flaky. `_confirm_and_close` now waits for the button to be enabled, clicks,
  then waits for the dialog container to disappear, re-clicking once if needed.
  Validated 3/3 clean runs on integration (~40s each).
