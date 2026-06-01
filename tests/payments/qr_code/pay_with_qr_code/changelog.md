# Changelog: Pay With QR Code

## 2026-06-01 — Migrated from automation-js (VCITA2-13758)

Migrated `automation-js/features/salsa/qr-code-payment.feature` (scenario "pay with QR
code") into `tests/payments/qr_code/` as an isolated subcategory.

### Structure
- New isolated subcategory `payments/qr_code` (slug `qr_code`, cleanup `always`).
- `_setup`: enables `client_portal_checkout_v2`, logs in, creates the client and a
  "display a fee" ($100, `charge_type=paid_non_secured`) appointment service via API, and
  connects the mock payment gateway.
- `pay_with_qr_code`: the end-to-end QR payment + back-office verification.

### Flow (zero scope loss vs legacy)
1. Open POS for the client, add the service.
2. Grab the Pay-with-QR `data-link` from the QR dialog.
3. Pay the link in a second tab via the mock gateway.
4. Confirm the POS QR dialog shows `payment-received` (realtime), click Done.
5. Verify the back-office payment: "Payment for Sale #1 - <service>", $100.00,
   Credit Card (Online), and the service item.

### Reuse
- `connect_mock_gateway` (tips_settings).
- `enable_features` + new shared `create_service` / `create_client` (account_api).
- BO verification parallels `offset_fees_helpers` (self-contained copy to keep the
  category independently stable; asserts the additional payment-type field).

### Waits
- Normal UI waits capped at 5s.
- The realtime QR-dialog `payment-received` push uses a ~90s eventual-consistency poll
  (legacy waited 90s; this was the legacy flake point — run 1 timed out, run 2 passed).
- Second-tab gateway round trip, QR-link population, and the BO cold load use load budgets.

### Baseline
- Legacy passing run: ~78.7s (flaky, 1/2 on integration).
