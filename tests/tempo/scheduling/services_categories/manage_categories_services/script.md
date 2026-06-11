# Script — manage_categories_services

`test_manage_categories_services(page, context)` orchestrates the helper actions
(`services_categories_actions`) and assertions (`services_categories_helpers`):

1. `create_category("category_one")`; `assert_categories([My Services=[Demo, In-office,
   Intro], category_one=[]])`.
2. `create_event_service("r2p_event", price=100, max_attendees=10)`;
   `create_appointment_service("Gong", category="category_one")`;
   `assert_service_details("r2p_event", contains=["$100","10 attendees"])`;
   `assert_service_details("Gong", contains=["1 on 1"], excludes=["$"])`.
3. `edit_service_category("In-office appointment", "category_one")`;
   `assert_categories([My Services=[r2p_event, Demo, Intro], category_one=[Gong,
   In-office]])`.
4. `rename_category("category_one","New_name")`; `delete_service("Introductory phone
   call")`; `assert_categories([My Services=[r2p_event, Demo], New_name=[Gong,
   In-office]])`.
5. `move_category_up("New_name")`; `edit_service_name("In-office appointment",
   "service_one")`; `assert_categories([New_name=[Gong, service_one], My Services=
   [r2p_event, Demo]])`.
6. `clone_service("service_one")`; `assert_categories([New_name=[Gong, service_one, Copy
   of service_one], My Services=[r2p_event, Demo]])`.
7. `delete_category("My Services")`; `assert_categories([New_name=[Gong, service_one,
   Copy of service_one, r2p_event, Demo]])`.

## Helper notes

- All actions re-enter `/app/settings/services` before acting (mirrors the legacy page
  object) so each reads a freshly rendered list.
- Angular-Material menus / md-select / md-checkbox use JS clicks where overlays
  intercept the standard click.
- New 1-on-1 / event services set an explicit "Other address" (fresh account has no
  business address, so the default radio would fail validation).
- `delete_service` uses the service editor's Delete button (verified path) + Ok confirm.
- Reads scroll the endless-scroll list until the category-card count stabilises.
