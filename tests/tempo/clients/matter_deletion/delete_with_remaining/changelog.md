# Changelog - delete_with_remaining

## 2026-06-08 - Initial migration (VCITA2-13990)
- Migrated from `automation-js/features/steps/matter-deletion.feature`
  ("delete matter from a contact with other matters remaining").
- Setup creates the `contact last` contact via API (isolated account).
- Reuses `matters_management.matters_helpers` (open_matter_page, add_matter_from_pane) and
  `crm_filters.crm_filters_helpers` (open_clients_list, clear_all_filters, add_text_filter,
  assert_filtered_clients); the only new helper is `delete_matter` (API uid resolve +
  matter-detail More -> "Delete client" -> confirm, waiting on the DELETE response).
- Quality: zero scope loss vs legacy (add matter, delete matter, Email-filter assertion for
  remaining matter, delete last matter, Email-filter empty assertion).
