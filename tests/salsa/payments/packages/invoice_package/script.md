# Pay an invoiced single-service package — Detailed Script

## Actions
1. Create a fresh client via API (`make_client`).
2. Create package `single1` via UI (`create_package`: specific service `service`, 2cr, $150,
   expires 1 week — expiry is set on the API package only; the UI form doesn't change the
   asserted behavior, so the package is created with default expiry which does not affect the
   invoice->PAID assertion).
3. Assign `single1` to the client via the client card (`assign_package_via_client_card`).
4. Invoice the package from the client-package card (`invoice_client_package`): name
   `single1_invoice`, billing address `blablablabla` (Create invoice -> wizard).
5. Pay the invoice `single1_invoice #0000001` ($150) — reuses event_payments `pay_for_invoice`
   (open Billing & Invoicing order, take-payment record).
6. Assert client-package request: state PAID, amount $150.00, client first last, package single1.
   The invoice-pay -> PAID propagation is eventually consistent (the BO card transiently shows
   "Payment info is not available"), so `assert_client_package` is given `client_id` and first
   confirms PAID via an API read-back of the client-package's payment-request state, then reads
   the UI card once (≤2 UI retries, ≤5s each).
7. Assert Payments Received has "Payment for single1_invoice #0000001" (reuses
   cp_payment_actions `assert_payment_in_search`).

## Success Verification
- Client-package PAID $150.00 and the invoice payment is searchable.
