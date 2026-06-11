# Script — New Dashboard Widget Count

## Flow
1. `open_dashboard(page)` — navigate to `/app/dashboard` (goto bounded at 5s), wait for
   the dashboard `.main` section, then the first `[data-qa="EmbeddedAppDelegator"]` widget.
2. `assert_widget_count(page, 6)` — poll up to 5s until exactly 6 widgets render.

## Notes
- Widgets are top-level POV (frame `''`), verified live.
- new_dashboard FF is enabled by the dashboard category setup.
- All element waits bounded at 5s; `assert_widget_count` uses a bounded <=5s poll with a
  0.2s interval (poll cadence, not a blind sleep).
