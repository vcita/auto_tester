# Assign a recorded payment as an invoice deposit (Quick Actions)

Migrated from `automation-js/features/salsa/deposits.feature` scenario 1
("Business record multiple payments, creates an invoice, and assigns a payment as deposit").

## Objective
On an account without point_of_sale, record two payments via Quick Actions, create
and send an invoice with a $50 item, assign one recorded payment as the invoice
deposit, and verify the invoice total and deposit.

## Preconditions (from _setup)
- Logged in to the isolated account.
- Client "Torry Deposi" created via API.

## Steps
1. Deny the `point_of_sale` feature flag so Quick Actions exposes the Record-payment
   dialog (matches the legacy "deny feature flags" + re-login), then reload the dashboard.
2. Record a payment via Quick Actions for Torry Deposi: custom item `deposit_item`, amount `5`.
3. Record a second payment via Quick Actions: custom item `regular_item1`, amount `3`.
4. Create and send an invoice for Torry Deposi titled `deposit_invoice` with a custom
   item `big invoice` priced `50`, and assign the `Payment for deposit_item` payment as
   the deposit.

## Verification
- The invoice shows state **ISSUED**, amount **$45.00 (out of $50.00)**, and a deposit
  row of **$5.00**.
