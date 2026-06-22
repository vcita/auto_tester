# New Dashboard Widget Count

Migrated from `automation-js/features/tempo/app-widgets-manager.feature`
scenario **New dashboard loading** (VCITA2-13864).

## Steps
1. With the new_dashboard feature flag enabled (category setup), open the dashboard.
2. Verify the dashboard shows 6 widgets (`[data-qa="EmbeddedAppDelegator"]`).
