# Manage CRM Table Tabs

Migrated from `automation-js/features/steps/crm-tabs-management.feature`
(Scenario: "Manage CRM table tabs").

## Steps
1. Select the "New inquiries" CRM tab.
   - The CRM table shows its empty state.
   - The filtered-clients counter displays "0 CLIENTS".
2. Select the "Recently active" view from the views dropdown list.
   - Search "form_first" in the "Recently active" tab's search bar.
   - The result row is "form_first form_last (You as a client)".
   - The filtered-clients counter displays "1 CLIENTS".
3. Drag the "New inquiries" tab to precede the "All" tab.
   - The "New inquiries" tab is displayed before the "All" tab.
4. Close the "New inquiries" tab.
   - The "New inquiries" tab is then displayed in the views dropdown list.
