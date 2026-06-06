# Dashboard Setup — Script (HOW)

Source: `steps.md`. On the per-category auto account:

1. `enable_features(context, "new_dashboard")` — admin API + cache reset, so the
   dashboard renders the new-dashboard widgets (quick actions widget).
2. `fn_login(page, context, username, password)` — UI login.
