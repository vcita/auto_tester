# EU Strict Invoice Refund Credit Notes - Script

## Initial State
- User is logged in to the isolated Italy account.
- Client and paid service were created by the subcategory setup.

## Actions

### Step 1: Create invoice
- Open Billing & Invoicing from the Sales navigation.
- Click `New` and choose `Invoice`.
- Select the setup-created client.
- In the invoice editor iframe:
  - Set the invoice title.
  - Fill sender billing address with `Rome, Italy`.
  - Select the setup-created paid service.
  - Save the draft, then approve/send it from the invoice page.
- If the first-invoice setup dialog appears, enter the generated starting invoice number and save.

### Step 2: Assert invoice data
- Read invoice title, client, state, amount, and credit status from the invoice page.
- Prefer `data-qa` selectors from the legacy page object:
  - `[data-qa="payment_status_state"]`
  - `[data-qa="credit_status_badge"]`
  - `[data-qa="view_credit_notes"]`
- Use semantic heading/text fallbacks where `data-qa` is not available.

### Step 3: Search orders
- Open Billing & Invoicing.
- Fill the order search input with the invoice title.
- Poll visible order title rows until the invoice appears.

### Step 4: Record full cash payment
- Open the invoice by title from Billing & Invoicing.
- Click `Take payment`, choose `Record payment`, select `Cash`, and click `Record`.
- Wait for the dialog to close and verify the invoice is paid.

### Step 5: Refund payment
- Open Payments Received.
- Search for the invoice title and open the matching payment.
- Click the refund action, optionally fill a partial refund amount, and submit.
- Do not rely only on the success toast; verify the invoice state and credit notes afterward.

### Step 6: Credit-note assertions
- Open the invoice.
- Read `InvoiceViewModel.invoice.metadata.credit_notes` from the Angular invoice scope, matching the legacy assertion source.
- Assert credit-note count and amount values.
- Click `view_credit_notes` and verify a new PDF tab opens.

## Success Verification
- First invoice: issued, paid, fully refunded, credited, one credit note, PDF opens.
- Second invoice: issued, paid, two partial refunds, credited, two credit notes with `$60.00` and `$40.00`.
