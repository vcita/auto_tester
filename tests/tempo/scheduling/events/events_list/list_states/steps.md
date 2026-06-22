# Events list page — empty / one / two / filtered (list_states)

Migrated from `automation-js/features/tempo/events-list.feature` (VCITA2-13949), the
single scenario. The events-list rows render `<service title> <STATUS>`; each case
asserts the rendered list against the expected rows (the legacy assertion intent).

Prerequisite (from `_setup`): logged in on a fresh account with two event services —
`r2p_event<seq>` (require to pay) and `daf_event<seq>` (display a fee).

## WHAT the test verifies

1. **Empty state** — open the events list page and search with no filter; the list is
   empty (no event rows).
2. **One result (SCHEDULED)** — schedule an event from the events list page (the
   "+ new event" button) for `r2p_event`; the default (future) date keeps it SCHEDULED.
   Searching shows exactly `r2p_event<seq> SCHEDULED`.
3. **Two results (SCHEDULED + COMPLETED)** — schedule a second event from the list for
   `daf_event` with the start date moved to the previous month (so it lands in the past
   → COMPLETED). Searching shows `r2p_event<seq> SCHEDULED` and `daf_event<seq> COMPLETED`
   (future-first ordering).
4. **State filter (COMPLETED)** — apply the COMPLETED event-status filter; only
   `daf_event<seq> COMPLETED` is shown.

## In scope (UI) vs prerequisite (API)

- UI (in scope): scheduling an event from the events list page, and the
  search / state-filter / empty-state assertions on that page.
- API (prerequisite, done in `_setup`): creating the two event services.
