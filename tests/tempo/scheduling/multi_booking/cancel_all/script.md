# Cancel all multi-booking appointments — script

## Entry
`test_cancel_all(page, context)` — uses `mb_service_names`, `mb_client_name`,
`mb_client_id`.

## Locators (multi_booking_ui.py)
- Same scheduling + appointment locators as cancel_single.
- Cancel all: `[data-qa='cancel']` → nested Vue iframe →
  `[data-qa='bulk-action-multi-booking-footer-Confirm']` (leave default = all).
- Conversation bubble: navigate `/app/clients/<client_id>`; last bubble row
  `.bubble-row:last-child div.linked-booking-bubble`; services
  `span.msgbl-title`; labels `.msgbl-text-label` (one equals `CANCELLED`).

## Flow
1. Snapshot appointment ids (API), schedule the 3-service booking via UI.
2. Diff appointment ids → 3 new; map title→id.
3. Open service1 appointment → cancel all.
4. Re-open each of the 3 appointments → assert state CANCELLED.
5. Open the client conversation → assert the last linked-booking bubble lists the
   3 services and includes a CANCELLED label.

## Scope preservation vs legacy
- Preserves the legacy `conversation displays cancelled linked-booking bubble`
  assertion (3 services + CANCELLED) and the `meeting created with details`
  CANCELLED state for all three appointments.
- Cancel-all uses the same bulk-cancel dialog + Confirm (legacy
  `cancelMultiBookingAppointment(true)`).

## Notes / intentional differences
- Appointments opened by id via `/app/appointments/<id>` (ids resolved by diffing
  the appointments list before/after scheduling).
- The conversation bubble is read on the client page `/app/clients/<id>`, inside
  the `#vue_iframe_layout` Vue iframe (legacy `vue_iframe_layout`), matching the
  legacy conversation page object source of truth.
