# Client Approves Estimate In CP — Script

Reuses `tests/sales/estimates_helpers.py` (shared with the Estimates subcategory).
All CP selectors below were verified live on integration during migration.

## Setup (API)
- `eh.create_client(context)` -> {id, name, email, portal_token}.
- `eh.create_estimate_api(context, title="approveEstimate", client_id=client["id"],
  items=[{title:"service", amount:100, description:"", quantity:1},
         {title:"product_item200", amount:20, description:"short desc", quantity:1}])`
  -> {uid, title}; total 120.00.

## CP: open + assert pending
- `eh.open_cp_estimate_page(page, context, client["portal_token"])` opens the CP
  estimates list as the client (CP host, `#cp_iframe`).
- `eh.assert_cp_estimate(cp_page, title, price="120.00", client=name,
  items=[{name:"service", price:"100.00"}, {name:"product_item200", price:"20.00"}],
  status_actions=[r"Approve", r"Reject"])`. Leaves the detail page open.

## CP: approve
- `eh.cp_perform_estimate_action(cp_page, "approve")`:
  - LOCATOR DECISION: approve button `button[data-qa="approve"]` (verified live).
  - Confirmation dialog `.dialog-containter`, confirm button `button.approve-button-text`.
- `eh.assert_cp_estimate_status(cp_page, "Approved on")`: polls the CP detail body
  until "Approved on <date>" renders.

## Back-office assert
- `eh.open_bo_estimate(page, context, estimate["uid"])` then
  `eh.assert_bo_estimate(page, title, price="120.00", state="APPROVED", client=name,
  total="120.00", items=[{name:"service", price:"100.00"},
  {name:"product_item200", description:"short desc", price:"20.00"}])`.

## Wait strategy
- Same as the decline test: helper `UI_TIMEOUT` for clicks, conditional
  `NAV_TIMEOUT` polling for the CP iframe load and async "Approved on" status —
  no fixed sleeps.
