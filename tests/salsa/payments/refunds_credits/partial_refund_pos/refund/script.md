# POS Partial Refund - Detailed Script

## Actions
### Step 1: Open Checkout
- Click `Checkout` (or `Sales` then `Checkout`); wait for `**/app/pos**`.

### Step 2: Add custom item
- Click `Custom Item`, fill `Name*` = `custom_item`, `Price*` = `5`, click `Add`.

### Step 3: Select client
- Click `Select Client`; in the `iframe[title="angularjs"]` dialog pick `Torry Deposi`.

### Step 4: Checkout and record
- Click `Checkout`, choose `Record payment`; set `Payment received via` = `Cash`, click `Record`.
- Wait for `**/app/payments/transactions/**` (lands on payment page).

### Step 5: Partial refund
- `partial_refund_current_payment(page, "1")`: open refund (via `[data-qa="refund"]`, falling back to `[data-qa="ps-more-actions"]`), set the `VcCounter` refund amount to `1` (the dialog renders in a nested frame; the helper resolves the hosting frame), confirm `Mark as refunded`/`Refund`.

### Step 6: Verify
- `assert_payment_page` reads `div.summary-header h3`, `div.summary-header h2 span`, `.refund-amount`.

## Selector Notes
- `data-qa` first (`nav-sales`, `refund`, `ps-more-actions`, `VcCounter`, `vc-footer-*`).
- Payment-page name/amount/refund use stable Angular billing CSS (`summary-header`, `refund-amount`); candidate for adding `data-qa` to the product.
