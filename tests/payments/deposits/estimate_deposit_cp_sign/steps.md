# Client signs and pays an estimate deposit (client portal, mock gateway)

Migrated from `automation-js/features/salsa/deposits.feature` —
"Client signs, pays estimate's deposit and approve it".

## Preconditions (API + BO setup)
1. Connect the mock payment gateway (back office) so the client can pay online.
2. Create a payable product via API: `product21`, price `80`, description "description for payable item21".
3. Create an estimate via API for the client "Torry Deposi": title `bestimate_sign`, the `product21`
   item, billing address, `send_email=true`, `is_signature_required=true`.
4. Attach a `$10` fixed deposit request to the estimate (API), `can_client_pay=true`.

## Steps
1. As the client, open the client portal (JWT) and open the pending estimate.
2. Verify the estimate shows a deposit **DUE $10.00** with an "Approve & pay" action.
3. Sign the estimate (signature canvas) and pay the deposit through the mock gateway popup.
4. Verify the payment success page shows **Amount received: $10.00**.
5. Re-open the estimate from the approved ("done") tab.
6. Verify the deposit now shows **PAID $10.00**.

## Notes
- The estimate is created via API (matches legacy) and resolved dynamically (the account is
  shared across the subcategory, so the estimate number is not `#0000001`).
- The mock gateway opens an external popup window; the deposit is paid by submitting it.
