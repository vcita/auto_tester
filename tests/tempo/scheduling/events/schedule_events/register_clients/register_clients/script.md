# Script — register clients to an event

Playwright-oriented HOW. Migrated from scheduling-events.feature scenario 1 (VCITA2-14026).
Implemented in `test.py`; shared UI/API logic lives in
`tests/scheduling/events/schedule_events/schedule_events_ui.py`.

## Setup (`_setup/test.py`, API)
- `fn_login` to the isolated account.
- `create_event_service` (event_payments_api): "require to pay" (`paid_force`) $100,
  `TLV`, max 2, USD — owner staff assigned (mirrors legacy Background order).
- `create_platform_staff_via_api` "user_staff".
- `create_client` x2 (silvan goodbye, judi babish-moshe), capturing portal tokens.

## Test
1. **Schedule (UI)** — `schedule_event_ui`: Calendar → New → Group event → select the
   API service (`[data-qa="service-select-input"]` / combobox option) → date picker next
   month → day `10` → assign `user_staff` (`.staff-selection` / staff combobox option) →
   submit (`[data-qa="dialog-submit-button"]`). The event uid is resolved via
   `GET /v2/event_instances` (the UI does not expose it).
2. **Assert details** — `read_event_details` opens `/app/events/{uid}` and reads the
   summary header (`h3` name, `h2` date), `[data-qa="booking-where"]` (location), the
   state chip, `.attendance-summary-row`, `.more-details span` and the `.attendance-list`
   names. Assertions (robust, not index-fragile):
   - name == service name; location == `TLV`; state == `SCHEDULED`;
   - date text contains the next-month name and day `10`;
   - attendance summary contains `0` and `2` (`0/ 2 Registered`);
   - more-details text contains `$100.00`, `Available on service menu`, `user_staff`;
   - attendees list empty.
3. **Register (UI)** — `register_clients_ui`: Register Clients → for each name, search
   (`Search by name, email or tag`) + pick the result → Continue → Send.
4. **Assert attendees** — `read_event_details` again; attendee name set equals
   {silvan goodbye, judi babish-moshe} (legacy matches by name, order-independent).
5. **CP conversation** — `assert_cp_conversation_title` opens the CP as silvan
   (`?client_jwt=<token>`), opens chat, asserts a `[data-qa="bubble-header"]` includes
   `Event Registration: <event>`.

## Waits / stability
- Navigation + cross-iframe readiness use the documented bounded `PAGE_TIMEOUT`/
  `NAV_TIMEOUT` (10s) exception; pure element waits stay at `UI_TIMEOUT` (5s).
- The event uid resolves through a bounded API poll (event-instance indexing can lag the
  UI create).
- CP runs in a fresh browser context (external vitrage) with the documented CP budget.
