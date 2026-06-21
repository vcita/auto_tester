# Changelog

## 2026-06-19 - Initial migration (VCITA2-14250)
**Phase**: All files
**Reason**: Migrated from automation-js features/salsa/packages.feature (back-office package management).
**Changes**:
- Created steps.md, script.md, test.py from the legacy scenario via MCP-verified exploration of the current build.
- Reuses tests/salsa/payments/packages/packages_helpers.py (BO package management UI) and shared helpers (account_api, appointment_payments_helpers, cp_payment_actions_helpers, event_payments_helpers).

## 2026-06-19 - Stabilization (VCITA2-14250): POS sale path gone for client-packages
**Phase**: test.py, script.md, steps.md, packages_helpers.py
**Reason**: The original POS flow (`pay_client_package_via_pos` reusing the event/appointment
`checkout-actions-activator` POS sale page) timed out with "POS checkout activator did not appear".
Live verification (two runs, screenshots) showed that on the current build a client-package
"Take payment" CTA opens the Take Payment dialog DIRECTLY (Send link / Send invoice / Charge card
/ Record payment) — there is NO POS sale page (`checkout-actions-activator`) for a client-package,
whether `point_of_sale` is enabled or not. Consequently the legacy POS "Payment for Sale #N -
bundle1" title is no longer reachable from the client-package surface; recording the balance emits
the standard "Payment for bundle1 - Package purchased" title (confirmed in Payments Received).
**Changes**:
- `pay_client_package_via_pos` now pays the full balance through the real BO Take-payment record
  dialog (reusing `cp_payment_actions_helpers.record_package_payment`), instead of the removed POS
  sale page. The real BO take-payment UI action is preserved (no API shortcut).
- Step 6 asserts the actual emitted title "Payment for bundle1 - Package purchased". Preserved
  coverage: the full balance is paid via a real BO take-payment action and the payment is
  searchable in Payments Received. Documented product-behavior change (not scope reduction).
- Step 5 PAID assertion now goes through the API read-back (see helpers changelog).
