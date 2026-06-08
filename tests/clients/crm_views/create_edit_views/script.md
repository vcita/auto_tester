# Create And Edit Views — Script

## Function
`test_create_edit_views(page, context)` in `create_edit_views/test.py`.
Helpers in `tests/clients/crm_views/crm_views_helpers.py`.

## Selector strategy (data-qa first, ported from legacy newClients.js)
- New view: `[data-qa="new-button"]` → `[data-qa="more-actions-button_add_custom_view"]`.
- View form: name `[data-qa="crm-save-view-modal-input-view-name"]`, description
  `[data-qa="crm-save-view-modal-input-view-description"]`, level segment
  `[data-qa="crm-save-view-modal-segment-level-item-account|staff"]`, save
  `[data-qa="vc-footer-Save"]`; delete confirm `[data-qa="vc-footer-Delete"]`.
- Tab `[data-qa="VcTabs-tab-<name>"]` (name spaces → `-` or removed; both variants tried).
- Close tab `[data-qa="VcTabs-close-<name>"]`.
- Views overflow dropdown `[data-qa="crm-view-more-button"]`; item `[name="<view>"]`.
- Three-dot menu trigger `[data-qa="VcTabs-VcDropdown-more-tab-<name>-three-dots"]`;
  menu body `[data-qa="VcTabs-VcDropdown-more-tab-<name>-header"]`; edit action
  `[data-qa="VcTabs-tab-<name>-actionItem-0"]`, delete action `...-actionItem-1`.
- All view panels are scoped under `.v-window-item--active` (Vuetify keeps every
  visited view mounted), matching the crm_filters pattern.

## Menu-text contract (legacy getThreeDotMenuTexts)
`view_menu_texts` opens the three-dot menu and splits the menu body inner_text by
newline (blank lines dropped):
- line[0] = description.
- permission line = "View is visible to all staff" (account) / "View is visible only
  to you" (staff).
- "View can't be edited or deleted" present when the staff cannot edit/delete the view.
Assertions match by line content (description == line[0]; permission/not-editable via
membership), which is robust to incidental extra lines.

## Flow (HOW)
1. `create_view` ×3 (account view/desc1/account, account view 2/desc2/account, staff
   view/desc3/staff): New → add custom view → fill form → Save → wait modal hidden +
   the new tab visible.
2. `assert_view_description`/`assert_view_permission` open each view's menu and check
   the lines.
3. `switch_to_staff(owner, staff_user)`: DELETE owner sessions, SSO-login as staff
   (`/v1/partners/sso/login`), wait dashboard. Then `close_tab("New inquiries")`,
   `select_view("account view")` (tab if pinned, else overflow dropdown).
4. `assert_view_not_available("staff view")` (no tab + not in overflow dropdown);
   `assert_view_not_editable("account view")` (menu shows the not-editable line).
5. `login_as_admin(owner)`: SSO-login as owner.
6. `edit_view("account view" → "now staff", "description1 new", staff)` via the
   three-dot Edit action; verify updated description + staff permission.
7. `delete_view("staff view")` via three-dot Delete + confirm; assert not available.
8. `switch_to_staff` again; assert `now staff` not available (staff-level owned by
   admin) and `account view 2` not editable by the staff.

## Waits
- Every locator wait/`expect` is capped at 5s (UI_TIMEOUT/CLIENTS_PAGE_TIMEOUT). No
  fixed sleeps; no retry loops. `page.goto` uses an explicit 5s timeout.
