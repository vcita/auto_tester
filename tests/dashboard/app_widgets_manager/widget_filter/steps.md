# Sales Widget Feature-Flag Filter

Migrated from `automation-js/features/tempo/app-widgets-manager.feature`
scenario **widget filter** (VCITA2-13864).

## Steps
1. Deny the `payments_module` feature flag (API), reload the dashboard.
2. Verify the dashboard shows 5 widgets and the sales widget is not shown.
3. Add the `payments_module` feature flag back (API), reload the dashboard.
4. Verify the sales widget is shown.
