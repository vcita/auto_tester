# Changelog: External receipt - POS

## 2026-06-08 — Created (VCITA2-13903)
- Migrated legacy "Create payment while using external receipt app - with pos". Reuses
  `deposits_pos_ui.record_pos_custom_payment` (POS custom item + Cash sale) via a
  `deposit_client_name` context alias, plus `gateway_setups_ui` payment-page + external-
  receipt assertions. Payment title `Payment for Sale #1 - some_item`; external receipt
  verified by the View-receipt new-tab URL containing `this-is-a-receipt-for-pdf-`.

## Wait audit (pre-PR)
- `NEW_TAB_TIMEOUT=15s` (gateway_setups_ui): justified — external mockreceipts redirect
  opens in a new tab; all other element waits are capped at 5s.
