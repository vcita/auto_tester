# Assign a recorded payment as an invoice deposit (POS)

Migrated from `automation-js/features/salsa/deposits.feature` scenario 2
("Business record multiple payments via POS, creates an invoice, and assigns a payment as deposit").

## Objective
With point_of_sale enabled (default), record two custom payments through the POS, create
and send an invoice with a $50 item, assign one POS sale payment as the invoice deposit,
and verify the invoice total and deposit.

## Preconditions (from _setup)
- Logged in to the isolated account (point_of_sale enabled by default).
- Client "Torry Deposi" created via API.

## Steps
1. Open the POS for Torry Deposi (Quick Actions -> Take payment), create a custom item
   `deposit_item` priced `5`, and record a Cash payment (creates Sale #1).
2. Repeat for a custom item `regular_item1` priced `3` (creates Sale #2).
3. Create and send an invoice for Torry Deposi titled `deposit_invoice` with a custom
   item `big invoice` priced `50`, and assign the `Payment for Sale #1 - deposit_item`
   payment as the deposit.

## Verification
- The invoice shows state **ISSUED**, amount **$45.00 (out of $50.00)**, and a deposit
  row of **$5.00**.
