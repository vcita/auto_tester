# Script: Unregister from BO and CP, then pay via POS

Playwright-oriented implementation notes for `test.py`. UI helpers live in
`tests/scheduling/events/schedule_events/schedule_events_ui.py`; payment + POS + CP
selectors are reused from `tests/payments/event_payments/event_payments_helpers.py`.

Identical to the sibling `unregister_online` flow except the final payment is taken
through Point of Sale (`pay_for_attendee_bo(..., pos=True)`); `point_of_sale` stays
enabled (the default) so `take_payment` opens POS.

## Implementation

1. **Register clients** — `register_clients_ui(page, context, event_uid, [silvan, judi, nir])`.
2. **Counter + table** — `attendees_counter(...)`; `read_attendees(...)` parses the unpaid
   (`.solo-attendees-list`) then paid (`.attendees-list`) lists; `find_attendee` matches by name.
3. **BO unregister** — `unregister_attendee_bo(page, context, event_uid, "judi babish-moshe")`.
4. **CP self-cancel** — `cp_self_cancel_meeting(page, context, silvan_token, service_name)`;
   the post-cancel table read uses `refresh=True` (re-navigate via Event List) to observe the
   out-of-band cancel.
5. **POS payment** — `pay_for_attendee_bo(page, context, event_uid, "nir karpin", "100",
   pos=True)` opens the attendee's payment status (`gotoPaymentStatus`), then take payment →
   POS checkout → Record payment → Cash → confirm; gated on the payment status reaching PAID.

## Comment assertion

`_assert_attendees` checks `payment_status`/`state`/`index_per_category` strictly and the
`comment` by canceller category: `""` (registered), `"Canceled by client"` (CP cancel), or
any `"Canceled by …"` (back-office/staff cancel).
