# Setup: Invoice Follow-up Tip

Mirrors tips.feature scenario "create invoice and add follow up tip - BO - charge".

1. Enable tips feature flags.
2. Assign the `tips` app (Admin auth).
3. Set tip options `10,20,30` + enable tips for BO (POST /platform/v1/payment/settings, read-back).
4. Create client `first last`.
5. Create an invoice (`invoice` → server title `invoice #0000001`) with a saved
   `product_item200` line ($20) and billing address `persepolis, persia`.
6. Record a $20 Cash payment for the invoice via API so it is fully paid
   (prerequisite for the invoice "Add a tip" follow-up action).
7. Log in to the back office.
8. Connect the mock payment gateway via the providers UI (required for the charge tip).
