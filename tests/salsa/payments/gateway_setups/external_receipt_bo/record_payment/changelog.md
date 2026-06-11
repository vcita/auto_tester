# Changelog: External receipt - back office

## 2026-06-08 — Created (VCITA2-13903)
- Migrated legacy "Create payment while using external receipt app". Reuses
  `deposits_invoice_ui.record_custom_payment` (BO Quick Actions record, custom item, Cash)
  via a `deposit_client_name` context alias, plus new `gateway_setups_ui` payment-page +
  external-receipt assertions. External receipt verified by the View-receipt new-tab URL
  containing `this-is-a-receipt-for-pdf-` (legacy parity).

## Wait audit (pre-PR)
- `NEW_TAB_TIMEOUT=15s` (gateway_setups_ui): justified — the View-receipt link opens the
  external mockreceipts redirect in a new browser tab; capturing/loading that external
  navigation needs a bounded budget above 5s. All other element waits are capped at 5s.
