# Set Up Invoice Late Fee (UI + Client Portal) - Script

## Initial State
- Logged in to the isolated US account (from _setup).
- Client `first last` (with portal token) and a `display a fee` service ($100) exist.

## Actions
1. **Late-fee settings (UI)** — `set_amount_late_fee(page, amount="10", days="5")`:
   navigate to `billing_and_invoicing?tab=invoices_and_estimates`, enable the toggle,
   pick the amount radio, fill amount + days, save (waits on the `/v2/settings` PUT).
   `assert_late_fee_enabled(page)` re-opens the tab and confirms persistence.
2. **Create + send invoice (UI)** — `create_and_send_invoice(..., existing_items=[service],
   enable_late_fee=True)`: opens the New > Invoice wizard, sets the title, adds the service
   item, sets the billing address, expands the terms section and ticks the late-fee
   checkbox, then sends (ISSUED).
3. **Business invoice assertion** — `assert_invoice_page(title="new_invoice", number=1,
   client="first last", state="ISSUED", amount="$100.00", late_fee="Subject to late fees")`.
4. **Client portal** — `open_portal(page, context, portal_token)` (fresh context via
   client_jwt) -> `open_pending_invoice(cp_page, "new_invoice #0000001")` (Payments ->
   Pending -> open the request).
5. **CP invoice assertion** — `assert_cp_invoice(invoice_name="new_invoice #0000001",
   client="first last", price="$100.00", late_fee="Late fees")`.

## Success Verification
- BO invoice page: name/client/ISSUED/$100.00/"Subject to late fees".
- CP invoice page: name/client/$100.00/"Late fees".

## Waits / Stability
- Settings save: wait on the `/v2/settings` 2xx response (true persistence, no reload).
- Invoice send: `send_invoice` waits for `/app/invoices/**`; first-invoice numbering dialog
  handled once.
- BO assertion polls the invoice page (issue + indexing lag).
- CP: navigation/list readiness uses a longer bounded budget; the entity page body is
  polled for the expected tokens before asserting the late-fee caption.

## Quality vs legacy
- Adds an explicit late-fee persistence re-check (`assert_late_fee_enabled`); the legacy
  relied only on the save success toast.
