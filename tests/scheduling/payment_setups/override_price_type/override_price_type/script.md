# Override Price Type — Script

Migrated from `payment-setups.feature` scenario "Update payment type during scheduling".

## Flow

1. **Setup (`_setup/test.py`)** — create client + the six payment-setting services via API
   (`create_service_via_api` with `charge_type_for(setting)`), then log in. No gateway:
   appointment-level price overrides never use online/require-payment, only the meeting price.

2. **Schedule each appointment with a price override** (`schedule_appointment(..., price_override=…)`):
   open the dialog's **Price** expansion panel, set the **Price options** select
   (`.fee-type-method-selector`), and fill the amount (`[data-qa='price-input'] input`) for
   fixed prices. Appointments collapse the six settings to three fee types:

   | service     | override price_type | fee type      | amount | expected meeting price |
   |-------------|---------------------|---------------|--------|------------------------|
   | require2pay | display free        | No Fee        | —      | Free                   |
   | suggest2pay | display for a fee   | Custom price  | —      | (blank)                |
   | displayFee  | dont display        | Custom price  | —      | (blank)                |
   | variedPrice | require to pay      | Fixed price   | 65     | 65 USD                 |
   | displayFree | display a fee       | Fixed price   | 97     | 97 USD                 |
   | noDisplay   | suggest to pay      | Fixed price   | 25     | 25 USD                 |

3. **Verify the meeting price** for each appointment (`read_meeting_price`).

## Locator decisions

- **Price panel** — `.dialog-expansion-panel__price .v-expansion-panel` (legacy
  `priceExpansionPanel`); expand via the header when `aria-expanded != true`.
- **Fee type** — `.fee-type-method-selector` (legacy `feeTypeSelect`); the menu items are
  Vuetify list items whose accessible name includes a description line, so the option is
  matched on its `.v-list-item__title` text (No Fee / Custom price / Fixed price) rather than
  the full option name.
- **Amount** — `[data-qa='price-input'] input` (legacy `priceInput`).
- **Meeting price** — same `read_meeting_price` as scenario 1.

## Verified

- 2026-06-09: focused run PASSED (2/2). Fee-type select options render with subtitles, so
  exact-name option matching fails; matching the title text is required.
