# Changelog: Event payment request lifecycle

## 2026-06-06 — Initial migration (VCITA2-13856)
- Migrated event-payments.feature scenario 1 (payment request create/edit/cancel).
- Added isolated subcategory `payment_request_lifecycle` under
  `payments/event_payments` with API setup (event service + event + attendee) and
  the event-attendee payment-request navigation/assertion helpers.

## 2026-06-06 — New-dashboard (POV) navigation fix
- On new-dashboard accounts the event attendee menu no longer exposes the payment
  request. Reworked navigation to reach it via Billing & Invoicing -> Orders ->
  the `eventattendance` order row, which opens `/app/payments/orders/{uid}` with
  the legacy Angular payment-status view.
- Helpers now scan `page.frames` for the payment-status frame (POV wraps Angular in
  `iframe[data-qa="angular-iframe"]`), reload the Orders list on indexing lag, and
  cache the order detail URL so post-waive reads navigate directly (waived requests
  drop out of the default Orders list).
- Scenario 1 passing end-to-end (~36s).

## 2026-06-07 — Stabilize cancel -> CANCELLED rollup (10/10 stress)
- One in ten stress runs failed the Step 3 assertion with
  `state: (CANCELLED, DUE)`: the cancellation rollup propagates slower than the
  default `NAV_TIMEOUT` (10s) eventual-consistency poll.
- Added an optional `timeout_s` override to `assert_event_payment_request` and
  widened only the cancel transition to a documented 20s bounded poll (the
  request is re-opened each iteration so the re-render picks up the server-side
  state change). Other state assertions keep the default window.
- Re-validated: `payment_request_lifecycle` stress 10/10 STABLE on integration.
