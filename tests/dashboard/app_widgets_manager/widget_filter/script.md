# Script — Sales Widget Feature-Flag Filter

## Flow
1. `deny_features(context, "payments_module")` — blacklist the FF + reset cache.
2. `open_dashboard(page)` (reload) → `assert_widget_count(page, 5)` and
   `is_widget_shown(page, "sales")` is False.
3. `enable_features(context, "payments_module")` — whitelist the FF + reset cache.
4. `open_dashboard(page)` (reload) → `is_widget_shown(page, "sales")` is True.

## Notes
- `is_widget_shown` mirrors legacy `isWidgetFound`: gate on the dashboard `.main`
  section first, then a bounded 5s wait on `.sales-widget`, so a still-mounting grid is
  never read as an absent widget.
- The FF change is applied via the admin API (which also resets the features cache
  server-side) and a full dashboard reload, so the widget set re-renders from the new
  flag state.
- The flag is restored to enabled at the end, leaving the shared dashboard account
  in its default state.

## Wait policy
- `open_dashboard` goto bounded at 5s (`PAGE_TIMEOUT`); all element waits bounded at 5s.
- `assert_widget_count` polls the exact widget count on a bounded <=5s loop with a 0.2s
  poll interval (poll cadence, not a blind fixed sleep).
