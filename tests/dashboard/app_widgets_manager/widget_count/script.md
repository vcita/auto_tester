# Script — New Dashboard Widget Count

## Flow
1. `open_dashboard(page)` — navigate to `/app/dashboard`, wait for the first
   `[data-qa="EmbeddedAppDelegator"]` widget visible.
2. `assert_widget_count(page, 6)` — poll up to 5s until exactly 6 widgets render.

## Notes
- Widgets are top-level POV (frame `''`), verified live.
- new_dashboard FF is enabled by the dashboard category setup.
