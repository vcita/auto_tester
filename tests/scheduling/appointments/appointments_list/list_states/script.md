# list_states — HOW (locators + flow)

Helpers: `tests/scheduling/appointments/appointments_list/appointments_list_helpers.py`.
API: `tests/account_api.py` (`create_appointment_via_api`, `future_appointment_start_time`)
plus the local `previous_month_appointment_start_time`.
Frames: outer `iframe[title="angularjs"]` → inner `#vue_iframe_layout` (Vue bookings page).
CP: vitrage `cp_iframe` (reuses the `reviews_cp_ui` open-portal + chat pattern).

## Locators (verified against frontage source)

| Purpose | Frame | Locator |
| --- | --- | --- |
| Filter search box | inner | `[data-qa="filter-search"]` (FilterSearch.vue) |
| Clear filters | inner | `role=button name="Clear filters"` (FilterPanel; JS click — `.button-area` is pointer-events:none) |
| Booking-status "Completed" | inner | `.booking-filter` CheckList item text "Completed" (BookingFilter.vue, `booking.status.completed`) |
| List rows | inner | `.booking-list-container .list-item` |
| Row service title | inner | row `.service-title` |
| Row status | inner | row `.status-text` (BookingStatus; text upper-cased for assertion) |
| Empty state | inner | `.booking-empty-state` (BookingListEmptyState.vue) |
| CP chat button | cp_iframe | `[data-qa="headerChatBtn"]` |
| CP conversation titles | cp_iframe | `[data-qa="bubble-header"]` |

## Flow

1. `open_appointment_list(page)` — navigate to `/app/appointment-list`, wait for
   `[data-qa="filter-search"]` (retries once on render race).
2. **Empty**: `search_appointments(page, [])` — clear filters, poll until rows == [] → assert `== []`.
3. **One**: `create_appointment_via_api(context, service, client, start_time=future_appointment_start_time())`
   (future → SCHEDULED) → `search_appointments(page, ["<service> SCHEDULED"])` → assert.
4. **Two**: `create_appointment_via_api(context, service, client, start_time=previous_month_appointment_start_time())`
   (prev-month day 10 → COMPLETED). Then:
   - `assert_cp_conversation_includes(page, context, client, "Appointment confirmed: <service>")`
     — open CP as the client, click chat, poll `[data-qa="bubble-header"]` (≤5s) for the title.
   - back on the appointment list, `search_appointments(page, ["<service> SCHEDULED", "<service> COMPLETED"])`
     → assert (start_time desc: the future SCHEDULED row precedes the past COMPLETED row).
5. **Filtered**: `search_appointments(page, ["<service> COMPLETED"], completed_filter=True)` → assert.

## Notes / decisions

- **Status normalization**: the rendered `.status-text` is translated (loaded from CDN); it is read
  live and upper-cased so the assertion is locale/CSS-independent while still verifying *which* status
  shows (preserves the legacy "SCHEDULED"/"COMPLETED" intent).
- **Ordering**: the list groups by month, sorted descending (BookingsPage `initialFilter` direction
  `desc`), so the future SCHEDULED appointment precedes the previous-month COMPLETED appointment —
  matching the legacy expected order.
- **Past date → COMPLETED**: the second appointment's start (and its auto-derived end) are in the
  previous month, so the booking renders COMPLETED (legacy `previous_month_10`).
- **CP conversation (the legacy @unstable risk)**: scheduling an appointment posts an "Appointment
  confirmed: <service>" activity to the client conversation asynchronously. The check opens the CP as
  the client and polls the conversation titles for ≤5s (async-indexing justification), like the legacy
  CP-UI assertion. If it is genuinely not produced on integration it is recorded as a risk in
  `changelog.md` — never silently dropped.
- **Waits**: all explicit waits use the 5s cap. `search_appointments` is a bounded readiness poll
  (≤5s, 250 ms steps) for the debounced list reload, not a reload-retry loop.
- **API setup vs UI**: appointment scheduling is API (legacy `user schedules new appointment via API`);
  the list assertions, the CP conversation check, and the export remain UI.
