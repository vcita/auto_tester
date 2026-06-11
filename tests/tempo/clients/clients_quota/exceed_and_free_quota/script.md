# Script — Exceed And Free Up Clients Quota

HOW the test drives the UI. Selectors live in `clients_quota_helpers.py` and are
sourced from the legacy page objects (NewClients, NewClientDialog, UpgradeDialog,
ImportClientsDialog, Layout).

## Frame topology
- **POV top-level page:** CRM list, "+ New" menu, "More actions" menu, the upsell
  dialog, the left dashboard menu item, and the quota system notification.
- **Outer Angular frame** (`iframe[title="angularjs"]`): the new-client dialog (and
  its quota banner) and the import wizard.

## Flow
1. `create_client_via_ui(page, "first11", "last11", "test11+<seq>@vmeetme.com")`
   - `open_clients_list` → "+ New" (`[data-qa="new-button"]`) → "New client"
     (`[data-qa="more-actions-button_new_matter"]`).
   - In the outer frame's `md-dialog.new-client-dialog-component`, type first/last/email
     (real keystrokes for Angular ng-model) and click Save (`//button/div[text()='Save']`).
   - Wait for the dialog's first-name field to detach (create committed).
2. `go_to_dashboard_from_menu(page)` → click `[data-qa="VcMenuItem-dashboard"]`, wait
   for `**/app/dashboard**`.
3. `assert_quota_notification(page)` → `[data-qa="vc-notification-clients_quota_exceeded"]`
   visible.
4. `assert_upgrade_dialog_on_new_client(page)` → open "+ New → New client"; expect
   `[data-qa="GenericUpsellDialog-upsell-modal"]`; close it.
5. `assert_upgrade_dialog_on_import(page)` → open "More actions → Import"
   (`[data-qa="more-actions-button"]` → `[data-qa="more-actions-button_matter_import"]`);
   expect the upsell dialog; close it.
6. `select_and_delete_client(page, "first10 last10")` → reuse crm_bulk_helpers
   `select_client` + `bulk_delete`.
7. `go_to_dashboard_from_menu(page)`.
8. `assert_new_client_dialog_banner(page)` → open the new-client dialog; expect
   `div.notification-message.announce`; Cancel.
9. `assert_import_wizard_opens(page)` → open import; expect `.import-contacts-wizard`.

## Waits
- All waits capped at 5s (project policy). No fixed sleeps; each step waits on an
  explicit condition (element visible/detached, URL, selection summary).
