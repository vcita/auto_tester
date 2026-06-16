# Changelog — no_payment_error

## 2026-06-07 — Initial migration (VCITA2-13901)
- Migrated payments_settings.feature scenario 4 (Online Payments - disable credit card).
- Asserts the provider banner, connects the mock gateway, disables credit-card payments
  via the API, and verifies the CP make-payment form surfaces the no-payment error dialog.
