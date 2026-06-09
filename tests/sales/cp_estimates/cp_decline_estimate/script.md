# Client Declines Estimate In CP — Script

Reuses `tests/sales/estimates_helpers.py` (shared with the Estimates subcategory).
All CP selectors below were verified live on integration during migration.

## Setup (API)
- `eh.create_client(context)` -> {id, name, email, portal_token}.
- `eh.create_estimate_api(context, title="rejectEstimate", client_id=client["id"],
  items=[{title:"product2", amount:10, description:"description for payable item2", quantity:1}])`
  -> {uid, title} (POST /platform/v1/estimates; free-form line item, no catalog needed).

## CP: open + assert pending
- `eh.open_cp_estimate_page(page, context, client["portal_token"])` opens the CP
  estimates list as the client in a fresh browser context (CP host
  `https://live.meet2know.com`, `#cp_iframe`).
- `eh.assert_cp_estimate(cp_page, title, price="10.00", client=name,
  items=[{name:"product2", price:"10.00"}], status_actions=[r"Approve", r"Reject"])`.
  This clicks the estimate title (`span.payment-title`) and leaves the detail page open.
  Pending detail shows the APPROVE / REJECT buttons.

## CP: decline
- `eh.cp_perform_estimate_action(cp_page, "decline")`:
  - LOCATOR DECISION: decline button `button[data-qa="estimate-decline"]` (verified live).
  - Confirmation dialog `.dialog-containter` (product spelling), confirm button
    `button.decline-button-text` (text "REJECT").
- `eh.assert_cp_estimate_status(cp_page, "Declined on")`: polls the CP detail body
  until the "Declined on <date>" status renders (capped at the helper NAV_TIMEOUT).

## Back-office assert
- `eh.open_bo_estimate(page, context, estimate["uid"])` then
  `eh.assert_bo_estimate(page, title, price="10.00", state="REJECTED", client=name,
  total="10.00", items=[{name:"product2", description:"description for payable item2", price:"10.00"}])`.

## Wait strategy
- All UI waits use the helper's 5s `UI_TIMEOUT`; `assert_cp_estimate` /
  `assert_cp_estimate_status` use the conditional `NAV_TIMEOUT` only for the
  CP iframe (re)load / async status render, polling for an explicit readiness
  signal (title+client text, status text) — not a fixed sleep.
