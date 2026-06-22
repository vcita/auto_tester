# Changelog — events_list / list_states

## 2026-06-08 — Initial migration (VCITA2-13949)

Migrated `automation-js/features/tempo/events-list.feature` (1 scenario) into
autotester as the isolated subcategory `scheduling/events/events_list`.

- **Setup (API):** create two event services — `r2p_event` (require to pay /
  `paid_force`) and `daf_event` (display a fee / `paid_non_secured`), price 1 — each
  confirmed with an independent GET read-back.
- **Test (UI):** verifies the events list page across four states:
  empty search, one SCHEDULED event scheduled from the list, two events
  (SCHEDULED + COMPLETED via a previous-month start date), and the COMPLETED filter.
- **Selectors:** `data-qa` first (`action-button-eventList-new_event`,
  `service-select-input`, `date-picker-text-input`, `dialog-submit-button`,
  `filter-search`); semantic/text fallbacks for the date picker, status filter, list
  rows (`.booking-list-container .list-item`, `.service-title`, `.status-text`) and
  empty state (`.booking-empty-state`).
- **Decisions:** status text read live + upper-cased (translations load from CDN);
  `search_events` uses a bounded ≤5s readiness poll for the debounced list reload;
  Clear-filters / Completed use JS click (`.button-area` is pointer-events:none).
