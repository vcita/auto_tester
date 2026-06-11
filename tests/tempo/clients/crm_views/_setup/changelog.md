# Changelog — CRM Views Setup

## 2026-06-08 — Initial migration (VCITA2-13951)
- Created `_setup` for the isolated `crm_views` subcategory.
- Mirrors legacy Background: capture owner staff, create one user-role staff
  ("Staff User") via Platform API, admin UI login, close the 3 default CRM tabs
  ("New inquiries", "Open payments", "All").
- Reuses `account_api.create_platform_staff_via_api` (POST + GET read-back) and
  `tests/_functions/login.fn_login`.
