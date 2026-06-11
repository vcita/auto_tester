# Changelog — register_clients (VCITA2-14026)

## 2026-06-10 — Initial migration (scenario 1)
- Migrated scheduling-events.feature scenario 1 "create a single event and register
  multiple clients to it" into an isolated child group under
  `tests/scheduling/events/schedule_events/`.
- Background seeded via API (reusing `event_payments_api.create_event_service`,
  `account_api.create_platform_staff_via_api`, `account_api.create_client`): a
  require-to-pay $100 event service, `user_staff`, and two clients.
- New UI helpers in `schedule_events_ui.py`: `schedule_event_ui` (BO schedule, next
  month day 10, assign staff), `read_event_details`, `register_clients_ui`,
  `assert_cp_conversation_title` (token-parameterized CP variant).
- Event uid resolved via `GET /v2/event_instances` (the UI does not expose it).
- Detail assertions kept robust (substring on more-details / date) rather than
  index-fragile `.more-details span[n]`, preserving the legacy field coverage
  (location, date, state, price, currency, staff, registration availability,
  attendance summary, attendees).
- Pending first focused run against integration to validate live selectors (event
  dialog staff selection, details field rendering, register picker).
