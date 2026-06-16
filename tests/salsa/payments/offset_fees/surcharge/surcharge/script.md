# Script: Surcharge

Helpers: `offset_fees_helpers` (fee config + Back Office), `offset_fees_checkout`
(client-portal checkout). All explicit waits are capped at 5s.

## 1. Enable surcharge (POV Online Payments tab)
- `enable_surcharge(page, context)`
- Tab: `{base}/app/settings/payments?tab=online-payments`
- Radio group `[data-qa="online-payments-tab-offset-card-fees-radio-group"]`
- Mode input `input[value='surcharge_fee']` (DOM click on label); no value input - product default 3%
- Acknowledge `[data-qa="online-payments-tab-offset-card-fees-acknowledgement-checkbox"] label`
- Save `[data-qa="online-payments-tab-header-saveButton"]`

## 2. Client-portal checkout (vitrage `cp_iframe`)
- `open_client_portal`: `{vitrage}/site/{pivot_uid}/action?client_jwt={token}`; ready `.quick-actions, .matter-picker`
- `open_past_meeting_payment`: bookings `[data-qa="client-area-menu-bookings"]`, past tab
  `[data-qa="tab-selector-past"]`, item `.booking-list-item.list-item` by `.booking-title`,
  meeting action `.action.v-btn .v-btn__content` text Pay. The redesigned checkout opens
  the dialog directly; an intermediate Pay button (`button[data-qa='payButton']`) is only
  pressed if the checkout dialog/proceed action is not already shown.

## 3. Checkout assertions (inside `.checkout-dialog`)
- Fee badge `.payment-method-card.selected .payment-method-card__fee-badge` == `+ 3%` (whitespace-normalized)
- Summary `.summary` contains `Surcharge` and `$3.00`
- Processing-fee line: `.summary` text matches /surcharge|convenience/i
- Proceed `[data-qa="perform-payment-action"]`
- Success `.done-loading[data-qa='payment-success-page']`; title `span.briliant`;
  amount `span.paymet-text` contains `$103.00`

## 4. Back Office (`/app/payments/transactions`)
- `assert_back_office_payment(page, context, "$103.00", "$3.00", [service])`
- Scope: top-level or `iframe[title="angularjs"]`
- Search `input[name="name_filter"]` -> first name; open list link by service name
- name `div.summary-header h3`; amount `div.summary-header h2 span`;
  client `span.contact-name, div .display-name-component span`;
  items `span.invoice-item-content-title`;
  fee regex on `div.entity-summary-row`
