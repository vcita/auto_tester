# Changelog — cp_multi_booking/summary_component

## 2026-06-18 — Initial migration (VCITA2-14228)
- Phase: All files
- Author: migration (automation-js features/tempo/CP/multi-booking.feature)
- Reason: Migrate CP multi-booking coverage into autotester (team tempo, domain scheduling).
- Changes: created steps.md, script.md, test.py from the legacy step definitions and
  ClientPortal/Scheduler page objects; selectors quoted verbatim (data-qa first).

## 2026-06-18 — Staff-name deviation (focused run 1 fix)
- Run 1: summary staff assertion failed — legacy hardcodes "With Automation test business"
  but the autotester isolated account name varies per run.
- Fix: _setup resolves the owner staff display_name from the staff list; test asserts
  `f"With {owner_display_name}"` (account-name-agnostic, same behavior).
