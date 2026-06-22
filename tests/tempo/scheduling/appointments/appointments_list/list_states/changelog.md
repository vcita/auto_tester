# Changelog — appointments_list / list_states

## 2026-06-08 — Initial migration (VCITA2-13953)

Migrated `automation-js/features/tempo/appointments-list.feature` scenario 1
("Appointment list page - empty, with results, and filtered") into autotester as the
isolated subcategory `scheduling/appointments/appointments_list`.

- **Setup (API):** create one client (`first last`, capturing the CP portal token) and one
  appointment service (`service<seq>`), confirmed with an independent GET read-back.
- **Test (UI + API setup):**
  - Empty search → empty list.
  - Schedule one appointment via API (future date) → list shows `<service> SCHEDULED`.
  - Schedule a second appointment via API in the previous month (past → COMPLETED) →
    the client-portal conversation includes `Appointment confirmed: <service>`, and the
    list shows `<service> SCHEDULED` + `<service> COMPLETED` (future-first, `desc`).
  - COMPLETED status filter → only `<service> COMPLETED`.
- **UI vs API:** appointment scheduling is API setup (legacy `user schedules new
  appointment via API`); the list search/filter/empty-state assertions and the CP
  "Appointment confirmed" conversation check are kept UI (legacy verified them via UI).
- **Selectors:** `data-qa` first (`filter-search`, CP `headerChatBtn`/`bubble-header`);
  list rows `.booking-list-container .list-item` with `.service-title` + `.status-text`,
  empty state `.booking-empty-state`, "Clear filters" button and the booking-status
  "Completed" CheckList item (JS click — `.button-area` is pointer-events:none).
- **Decisions:** status text read live + upper-cased (translations load from CDN);
  `search_appointments` clears/applies a filter (which re-fetches bookings from the
  server, so API-created appointments appear) and polls ≤5s for the debounced reload.

### @unstable risk (legacy VCITA2-3361)

The legacy scenario is tagged `@unstable` ("fix issue in fenv", VCITA2-3361). It is
migrated in full and run on integration. The CP "Appointment confirmed" conversation
posts asynchronously, so the check polls the conversation titles for ≤5s (asynchronous
indexing justification) — a real CP-UI verification like the legacy test, not an API
shortcut. If this conversation is genuinely not produced on integration, it is recorded
here as a risk rather than silently dropped.

**Validation outcome (integration):** the CP "Appointment confirmed: <service>"
conversation IS produced and visible on integration. With the bounded ≤5s poll the step
passed on every focused run (3/3) and across the stress run — no flakiness observed. The
legacy `@unstable`/VCITA2-3361 risk did not reproduce on integration; no scope was dropped.
