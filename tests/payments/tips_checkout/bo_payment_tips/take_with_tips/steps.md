# Edit tips options & take payment with tips (BO)

Migrated from `automation-js/features/salsa/tips.feature` scenario 1
"edit tips options & take payment with tips".

## Steps

1. Close the client's payments balance (record, ACH, send receipt, tip **55%**).
   - The back-office payment page shows **first last**, **Payment for Multi-item
     #0000001**, **$387.50**, type **ACH**, items **service + package**, tip
     **$137.50** (55% of the $250 service + package balance).
2. Record a custom-item payment **some_item $5** with a **Custom** tip of **4.5**.
   - The back-office payment page shows **Payment for some_item** with tip **$4.50**.
