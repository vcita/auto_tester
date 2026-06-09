# Scheduling With Taxes

## Objective
Verify taxes applied to services and appointments produce the correct services-list tax text, meeting prices, and payment-request amounts (with tax math), including the tax_mode include behavior.

## Prerequisites
- Logged in to the isolated account with a client `first1 last1` (from `_setup`).

## Steps
1. Create three taxes via API: `default_tax` (10%, default for services), `non_default_tax` (5%), `another_tax` (15%).
2. Create a `suggest2pay` service ($50) via API.
3. Create three services via the UI: `require2pay` (require to pay, $100), `displayFree` (display free), and `another require` (require to pay, $100, with the non_default 5% tax).
4. Verify the services list:
   - `suggest2pay` → online, $50
   - `require2pay` → required, $100, (+10% Tax)  (default tax applied)
   - `displayFree` → free
   - `another require` → required, $100, (+15% Tax)
5. Schedule appointments: `require2pay`, `suggest2pay` (override tax to another_tax 15%), `displayFree`, `another require`.
6. Verify meeting details: `displayFree` → Free; `require2pay` → 110.00 ($100 + Tax).
7. Verify the appointment payment requests:
   - `require2pay` → DUE, $110.00 ($100.00 + Tax)
   - `suggest2pay` → NOT YET DUE, $57.50 ($50.00 + Tax)
   - `another require` → DUE, $115.00 ($100.00 + Tax)
8. Set tax_mode to `include` via API, schedule another `require2pay` appointment, and verify:
   - new appointment → DUE, $100.00 (tax-inclusive)
   - the earlier require2pay appointment still → DUE, $110.00 ($100.00 + Tax)

## Expected Result
- Services list shows the right tax text; meeting prices and payment requests reflect the correct tax math under both tax modes.

## Context Updates
- None (terminal scenario for this isolated subcategory).
