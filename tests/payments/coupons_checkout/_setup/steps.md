# Setup — Coupons in Checkout (isolated account)

Mirrors the account-level prerequisites of the legacy `coupons-pay.feature` Background,
on a fresh isolated account.

1. Log in to the isolated account (UI session is needed for the coupon-settings UI and
   the mock-gateway connection).
2. Create a 20% tax "TS" via API (`POST business/payments/v1/taxes`).
3. Create two "suggest to pay" ($100) appointment services "appointment_1" and
   "appointment_2", each taxed with "TS", via API (`POST /v2/settings/services`,
   charge_type `paid`, `tax_uids:[TS.id]`).
4. Connect the mock payment gateway via the UI (reuses `tips_settings.tips_gateway.connect_mock_gateway`).

Saves to context: `checkout_tax`, `checkout_services` ({appointment_1, appointment_2}).

The client and the two PAST appointments (legacy `previous_month_10`) are created
per-test, because each scenario pays a balance and that consumes it (all four tests
share this one isolated account).
