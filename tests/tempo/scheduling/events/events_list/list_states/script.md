# list_states — HOW (locators + flow)

Helpers: `tests/scheduling/events/events_list/events_list_helpers.py`.
Frames: outer `iframe[title="angularjs"]` → inner `#vue_iframe_layout` (Vue events page).

## Locators (verified against frontage source)

| Purpose | Frame | Locator |
| --- | --- | --- |
| "+ new event" button | outer (Angular) | `[data-qa="action-button-eventList-new_event"]` |
| Event dialog container | inner | `.event-dialog-container` |
| Service select (autocomplete) | inner | `[data-qa="service-select-input"]` (+ inner `input`) |
| Service option | inner | `role=option` filtered by service name |
| Start date text input | inner | `[data-qa="date-picker-text-input"]` (`.first`) |
| Date picker menu | inner | `.date-picker-menu-content` |
| Previous-month button | inner | `.date-picker-menu-content .v-date-picker-header button` (`.first`) |
| Day cell | inner | `.date-picker-menu-content .v-date-picker-table button` exact text "10" |
| Create Event (submit) | inner | `[data-qa="dialog-submit-button"]:not([disabled])` |
| Filter search box | inner | `[data-qa="filter-search"]` |
| Clear filters | inner | `role=button name="Clear filters"` (JS click — `.button-area` is pointer-events:none) |
| Event-status "Completed" | inner | `.event-filter` → text "Completed" (JS click) |
| List rows | inner | `.booking-list-container .list-item` |
| Row service title | inner | row `.service-title` |
| Row status | inner | row `.status-text` (BookingStatus; text upper-cased for assertion) |
| Empty state | inner | `.booking-empty-state` |

## Flow

1. `open_event_list(page)` — navigate to `/app/event-list`, wait for `[data-qa="filter-search"]`
   (retries once on render race).
2. **Empty**: `search_events(page, [])` — clear filters, poll until rows == [] → assert `== []`.
3. **One**: `schedule_event_from_list(page, r2p)` (default future date → SCHEDULED) →
   `search_events(page, ["<r2p> SCHEDULED"])` → assert.
4. **Two**: `schedule_event_from_list(page, daf, past_month=True)` (start = prev-month day 10
   → COMPLETED) → `search_events(page, ["<r2p> SCHEDULED", "<daf> COMPLETED"])` → assert.
5. **Filtered**: `search_events(page, ["<daf> COMPLETED"], completed_filter=True)` → assert.

## Notes / decisions

- **Status normalization**: the rendered `.status-text` is translated (loaded from CDN);
  it is read live and upper-cased so the assertion is locale/CSS-independent while still
  verifying *which* status shows (preserves the legacy "SCHEDULED"/"COMPLETED" intent).
- **Ordering**: the list groups by month, sorted descending, so the future `r2p` event
  precedes the previous-month `daf` event — matching the legacy expected order.
- **Waits**: all explicit waits use `UI_TIMEOUT` (5s). `search_events` is a bounded
  readiness poll (≤5s, 250 ms steps) for the debounced list reload, not a reload-retry loop.
- **Past date → COMPLETED**: moving the start date to the previous month also moves the
  auto-synced end date into the past, so the instance renders COMPLETED (legacy behavior).
