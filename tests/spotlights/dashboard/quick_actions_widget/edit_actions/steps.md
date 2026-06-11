# Edit Actions And Error Messages

Migrated from `automation-js/features/spotlights/quick_actions_widget.feature`
scenario **Quick actions widget - edit actions and error messages** (VCITA2-13863).

## Steps
1. Remove the `invoice` and `point_of_sale` quick actions (open edit modal,
   uncheck both, save).
2. Add the `event` quick action (open edit modal, check it, save).
3. Verify the widget displays: client, appointment, message, estimate, event.
4. Reorder `message` before `client` (drag message above client, save).
5. Verify the widget displays message immediately followed by client.
6. Uncheck all actions and save → an error message appears (min 1 action),
   then cancel.
7. Check all actions and save → an error message appears (max actions), then
   cancel.
