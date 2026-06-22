# Changelog

- Migrated legacy `Schedule from Calendar - Monthly display`.
- Preserved UI scheduling, recurring event, card assertions, and refresh state.

## 2026-06-10 - Stabilize New Appointment dialog load (shared helper)

**Phase**: Shared helper (`tests/scheduling/calendar/calendar_helpers.py`)
**Author**: Cursor AI
**Reason**: A headless `scheduling/calendar` stress run was flaky (~50% over 6 iterations). Screenshots showed the New Appointment editor opening but stuck on its loading spinner with a blank form body, so the single 5s wait before `_select_client` timed out (`TimeoutError: Timeout 5000ms exceeded`). Affected the appointment-heavy display tests (Monthly Display, Three Day Display, Display Multiple Staff).

**Changes**:

- Added `_wait_for_appointment_dialog_ready(angular)`, called right after clicking `option-new_appointment` and before `_select_client`. It polls the client-search field (the first interactive element, present only once the editor spinner clears) across a few bounded 5s windows before the existing reload recovery — mirroring `multi_booking`'s documented async New Appointment dialog handling.
- No scope/assertion change; gives the editor's async load more chances to settle within the 5s wait cap without bumping any individual timeout.

**Test run**: `scheduling/calendar` headless stress, 10 iterations — **6/10 passed (60%)**, up from ~50% pre-fix.

**Residual (not test-fixable)**: The remaining failures (runs 1/4/6/8) all show the New Appointment editor opening with a **blank body and a perpetual loading spinner** — the editor micro-frontend intermittently fails to load under integration load and does **not** recover even after the full-page reload retry. This is a product/environment-side hang, not a test-timing bug (legacy tagged this area `@unstable`). Real stabilization requires seeding the display-test appointments via API setup instead of the UI dialog (pending decision), or accepting it as known infra flakiness.

## 2026-06-10 - Widen New Appointment editor-ready window (shared helper)

**Phase**: Shared helper (`tests/scheduling/calendar/calendar_helpers.py`)
**Author**: Cursor AI
**Reason**: A follow-up 10x headless stress run reproduced the spinner failure here (run 10, 32.5s, blank spinner screenshot). Root cause refined: the editor-ready wait was only `UI_TIMEOUT` (5s), so a **slow-but-healthy** editor data fetch under integration load was misclassified as a stall — the reload-reset recovery then restarted the fetch from scratch on every retry, guaranteeing failure. Not a true hang.

**Changes**:

- Added `APPOINTMENT_EDITOR_READY_TIMEOUT` (15s) and used it in `_wait_for_appointment_dialog_ready`. A healthy editor still returns in ~1s; a slow fetch now completes within the window instead of being destroyed by a premature reload. The bounded reload-retry remains for a genuine hang.

**Test run**: `scheduling/calendar` headless stress, 10 iterations — **10/10 passed (100%, STABLE)**, up from 6/10.
