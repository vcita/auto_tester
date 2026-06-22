# Schedule Service Default

## Objective
Verify the six service payment settings render correctly on the services list and that an appointment scheduled for each shows the expected meeting price.

## Prerequisites
- Logged in to the isolated account with a client `first1 last1` (from `_setup`).

## Steps
1. Create six services via the UI, one per payment setting:
   - `require2pay` — require to pay, $100
   - `suggest2pay` — suggest to pay, $50
   - `displayFee` — display a fee, $10
   - `variedPrice` — display for a fee (no price)
   - `displayFree` — display free (no price)
   - `noDisplay` — dont display (no price)
2. On the services list, verify each service's payment type and price:
   - `require2pay` → required, $100
   - `suggest2pay` → online, $50
   - `displayFee` → online, $10
   - `variedPrice` → for a fee
   - `displayFree` → free
   - `noDisplay` → dont display
3. Schedule an appointment for `first1 last1` for each of the six services.
4. Open each created appointment and verify the meeting price:
   - require2pay → 100, suggest2pay → 50, displayFee → 10
   - variedPrice → (blank), displayFree → Free, noDisplay → (blank)

## Expected Result
- Each service appears on the services list with the correct payment type and price.
- Each appointment shows the expected meeting price.

## Context Updates
- None (terminal scenario for this isolated subcategory).
