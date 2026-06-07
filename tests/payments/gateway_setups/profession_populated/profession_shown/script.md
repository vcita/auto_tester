# Script: Wizard - populated profession

- `payment_wizard_ui.open_payment_wizard(page)` → Getting-Started checklist
  (`[name="checklist"]` → `body.wizard-open` → `[data-qa='payments_settings']` →
  `[data-qa='open-payment-wizard-action']`), then wait for the Vue wizard get-paid step.
- `read_preliminary_profession(page)` → advance `[data-qa='get-paid-next']`, click
  `[data-qa='profession-autocomplete']`, read `.v-list-item__title`.
- Assert the value equals `Legal services`.
- Controls are resolved by scanning the page + every frame (the wizard is 3 iframes deep:
  POV → Angular → `vue_wizard_iframe`); waits ≤5s, wizard mount ≤20s.
