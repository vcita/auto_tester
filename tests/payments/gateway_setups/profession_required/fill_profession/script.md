# Script: Wizard - profession required

- `payment_wizard_ui.open_payment_wizard(page)` → open wizard from the checklist.
- `currency_next_disabled(page)` → advance `[data-qa='get-paid-next']`, read the `disabled`
  attribute on `[data-qa='set-currency-next']` (legacy `getPreliminaryNextButtonDisableState`);
  assert it is disabled.
- `fill_preliminary_profession(page, "Legal services")` → click `[data-qa='profession-autocomplete']`,
  type the profession, click `.v-list-item__title`, then `[data-qa='set-currency-next']`.
- `assert_mcc_dialog_present(page)` → wait for `[data-qa='vc-btn']` + the wizard `#app` root
  (legacy MCC dialog assertion). Frame-scan across the 3-level iframe; waits ≤5s, mount ≤20s.
