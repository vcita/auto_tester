# Script: Calendar Settings staff permissions

Phase 2 for the `staff_permissions` test. The side-nav layout is read in the Vuetage
settings iframe; staff creation and SSO session switching reuse the calendar API/helpers.

## Step 1: Owner side-nav layout

Navigate to `/app/settings/calendar_settings` and read the side-nav. `settings_tabs` is
the count of `.grouped-items__group__container__menu-item` under the side-nav
`data-qa="calendar-settings-page__main-layout_page-side-nav"`; `has_staff_select` is the
presence of `.staff-controller` (gated by `can_access_staff_management`).

VERIFIED PLAYWRIGHT CODE:

```python
open_calendar_settings_page(page)
owner_layout = read_settings_side_nav(page)
assert owner_layout == {"has_staff_select": "true", "settings_tabs": "4"}, owner_layout
```

## Step 2-3: Create a limited staff member and switch session to them

VERIFIED PLAYWRIGHT CODE:

```python
staff = create_platform_staff(context, "Staff User", unique_email("staff-u"), "user")
switch_logged_in_staff(page, context, staff)
```

## Step 4 / Verification: limited-staff side-nav layout

VERIFIED PLAYWRIGHT CODE:

```python
open_calendar_settings_page(page)
staff_layout = read_settings_side_nav(page)
assert staff_layout == {"has_staff_select": "false", "settings_tabs": "3"}, staff_layout
```
