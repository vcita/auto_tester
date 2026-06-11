# Script: Wizard - funnel v1 upgrade

- `payment_wizard_ui.open_payment_wizard(page)` → open wizard from the checklist.
- `try_connect_gateway(page)` → `[data-qa='get-paid-next']` → `[data-qa='set-currency-next']`
  → `[data-qa='vc-btn']` (confirm) → `[data-qa='third-party-gateways-link']` →
  `[data-qa='stripe-connect']` (legacy `tryConnectToPaymentGateway`).
- `assert_wizard_dialog_present(page, label="Upgrade")` → the funnel-v1 account surfaces the
  upgrade dialog; assert the wizard `#app` root is present (legacy upgrade-dialog assertion).
- Frame-scan across the 3-level iframe; waits ≤5s, wizard mount ≤20s.
