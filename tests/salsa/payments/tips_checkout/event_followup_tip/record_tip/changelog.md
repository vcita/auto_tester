# Changelog — event_followup_tip / record_tip

## Migration (VCITA2-13899)
Migrated from `automation-js/features/salsa/tips.feature`, scenario
"create event and add follow up tip from clients list - BO".

### Setup (API)
- `seed_event_followup_tip_account`: tips flags, `tips` app (Admin auth), tip options
  `10/20/30` enabled for BO (POST `/platform/v1/payment/settings` + read-back), client
  `first last`, a require-to-pay `r2p_event` event ($10) with the client registered, and
  a recorded $10 Cash payment for the attendance so it is fully paid (the prerequisite for
  the event "Add a tip" follow-up action). The EventAttendance id is resolved from the
  `event_attendances/bulk_create` response.
- UI: BO login only (the follow-up tip is recorded as Cash, so no gateway is needed).

### Test actions (UI under test)
- Open the paid event attendance payment page, click Add a tip, choose record, select a
  `Custom` `5` tip, confirm; assert the BO payment page: `Tip for r2p_event`, `$5.00`,
  `Cash`, item `r2p_event`, tip `$5.00`.

### Reused helpers
- `tips_checkout_bo.open_payment_transaction_page` (`/app/transactions/<uid>`) +
  `add_followup_tip` (record) + `assert_payment_page_with_tip`.

### Selector / navigation considerations
- The scenario title says "from clients list", but the legacy implementation reaches the
  payment page (event → attendee → gotoPaymentStatus → PaymentPage) and adds the tip
  there. This migration opens the same payment page directly via the paid attendance
  payment's transaction detail (`/app/transactions/<uid>`). The Billing & Invoicing Orders
  list defaults to an OVERDUE/DUE filter, so a pre-paid attendance order is not listed
  there — the transaction-detail route is the stable entry point and matches legacy
  `PaymentPage.addTipFromCurrentPayment`.
- Tip picker `md-select[name='tip_option']` + custom amount `input[name='tip_amount']`
  have no product data-qa; stable legacy selectors are reused and documented.
