# Client approves an estimate with an offline deposit (client portal)

Migrated from `automation-js/features/salsa/deposits.feature` —
"Business creates estimate with offline deposit, client approved it".

## Preconditions (API setup)
1. Create a payable product via API: `product21`, price `80`.
2. Create an estimate via API for "Torry Deposi": title `bestimate_offline`, the `product21` item,
   `send_email=true`.
3. Attach a `$10` fixed deposit request to the estimate (API) with `can_client_pay=false`
   (offline-only deposit). No online gateway is needed — an offline deposit is never paid online.

## Steps
1. As the client, open the client portal (JWT) and open the pending estimate.
2. Verify the estimate shows a deposit **DUE $10.00** with an "Approve" action only
   (no online "Approve & pay" — the deposit cannot be paid online).
3. Approve the estimate (confirm dialog).
4. Verify the client is redirected to the offline-deposit page showing **$10.00**.
5. Re-open the estimate from the approved ("done") tab.
6. Verify the deposit now shows **OFFLINE**.

## Notes
- The estimate is created via API and resolved dynamically (the account is shared across the
  subcategory, so the estimate number is not `#0000001`). Legacy created it via the BO UI; the
  BO UI estimate+deposit creation path is already covered by `estimate_deposit_bo`, so this
  scenario focuses on the client-portal offline-approval behavior (the distinct coverage here).
