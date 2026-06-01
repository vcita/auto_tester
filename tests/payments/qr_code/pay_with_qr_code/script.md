# Script: Pay With QR Code

Implementation notes for the QR payment flow. Controls are resolved across the page and
all frames (POV top document + Angular iframe) unless noted.

## Step 1 — Open POS for the client (`open_pos_with_client`)
- Ensure on `/app`; click Quick Actions (`.quick-actions button, [data-qa="vcMenu-QuickAction"]`).
- Wait for the menu (`[data-qa="VcQuickActions"]`), click Take payment
  (`[data-qa="VcLargeQuickAction-point_of_sale"]`).
- Client picker (Angular dialog): fill `div.search-clients input` with the client full
  name, click the first result (`.md-dialog-container [role="list"]:not([ng-hide]) .main-client-info`).

## Step 2 — Add service + grab QR link (`add_service_and_grab_qr_link`)
- Hover the catalog card (`[data-qa="catalog-item-<service>"]`) if the add button is not
  yet visible, then click add (`[data-qa="catalog-item-<service>"] [data-qa="add-item"]`,
  force=true). Confirm the billable item rendered (`.billable-item-container__name`).
- Open checkout actions (`[data-qa="checkout-actions-activator"]`) → Pay with QR
  (`[data-qa="checkout-action-qr"]`).
- Read the payment link from the QR container's `data-link`
  (`.payment-content[data-link]`). Poll until the attribute is populated (load budget).

## Step 3 — Pay the link in a second tab (`pay_link_in_new_tab`)
- `page.context.new_page()`, goto the grabbed link.
- Click `.continue-btn` (link checkout), then the mock gateway submit (`button[type=submit]`).
  A short-lived gateway popup may open and auto-close; it is tolerated.
- Wait for the success page (`[data-qa='payment-success-page'], span.briliant`), close the tab.

## Step 4 — Confirm QR dialog success (`confirm_qr_dialog_success`)
- The paid link pushes a realtime update to the open POS QR dialog. Poll for
  `[data-qa='payment-received']` with a long realtime budget (~90s — legacy waited 90s;
  this is eventual consistency, not a normal 5s element wait). Click Done
  (`[data-qa='vc-footer-Done']`).

## Step 5 — Back-office verification (`assert_back_office_payment`)
- Go to `/app/payments/transactions`; the AngularJS list renders inside the `angularjs`
  iframe and cold-loads after the cross-document round trip (page-load budget, ~15s).
- Fill the name filter (`input[name="name_filter"]`) with the client first name, click the
  list row whose title (`f-ellipsis-tooltip.payment-title .text`) contains the service.
- On the detail page assert:
  - name `div.summary-header h3` = "Payment for Sale #1 - <service>"
  - amount `div.summary-header h2 span` = $100.00
  - type `div.entity-summary-row .icon-v + div span.caption.wrap` = "Credit Card (Online)"
  - items `span.invoice-item-content-title` contains the service.

## Waits
- Normal UI controls: 5s cap.
- Second-tab gateway round trip + QR link population + BO cold load: load budgets (15–20s).
- Realtime QR-dialog `payment-received`: ~90s eventual-consistency poll (documented exception).
