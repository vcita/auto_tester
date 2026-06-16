# Exceed And Free Up Clients Quota

Migrated from `automation-js/features/steps/clients-quota.feature`
(Scenario: "Exceed and free up clients quota").

Account is isolated and capped at 11 clients (operator package, provisioned by the
runner). Setup seeded 10 clients via API, so the account starts at 10/11.

## Steps
1. **Reach the cap:** create the 11th client (`first11 last11`) via the new-CRM
   "+ New → New client" dialog. Account is now at 11/11.
2. Go to the dashboard from the left menu (lets system notifications refresh).
3. **Assert** the clients-quota system notification appears.
4. **Assert** the upsell/upgrade dialog appears when trying to create a new client
   from the new CRM (blocked at the cap).
5. **Assert** the upsell/upgrade dialog appears when trying to import clients from
   the new CRM (blocked at the cap).
6. **Free up quota:** select client `first10 last10` in the CRM and bulk-delete it.
   Account is now at 10/11.
7. Go to the dashboard from the left menu (refresh notifications).
8. **Assert** the new-client dialog quota banner appears (near-limit banner shown in
   the create dialog when below the cap).
9. **Assert** the import wizard opens from the new CRM (import allowed below the cap).

## Scope / fidelity notes
- All 5 legacy assertions are preserved: quota system notification, upgrade dialog on
  create, upgrade dialog on import, new-client dialog banner, import wizard opens.
- The 10 prerequisite clients are created via API in setup (out of scope); only the
  11th (cap-reaching) client is created through the UI, as in the legacy scenario.
