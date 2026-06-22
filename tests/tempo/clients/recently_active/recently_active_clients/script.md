# Recently Active Clients - Detailed Script

> **Status**: Migrated from automation-js mapping
> **Last Updated**: 2026-05-24
> **Source**: `automation-js/features/steps/clients-recently-active.feature`

## Initial State
- User is logged in by the clients category setup.
- The test uses account API setup for service, clients, and appointments, matching the legacy scenario.
- UI coverage is focused on the dashboard recently active clients widget.

## Test Data
```python
timestamp = int(time.time())
service_name = f"Recently Active Service {timestamp}"
first_client_data = {
    "first_name": "first",
    "last_name": "last",
    "email": f"recent.first.{timestamp}@vcita-test.com",
}
second_client_data = {
    "first_name": "first2",
    "last_name": "last2",
    "email": f"recent.second.{timestamp}@vcita-test.com",
}
```

## Actions

### Step 1: Create Service
- Read the account business UID from `context["auto_account"]`.
- Fetch categories from `/platform/v1/categories`.
- Fetch the first staff member from `/platform/v1/businesses/{business_uid}/staffs`.
- Post a free appointment service to `/v2/settings/services`.
- Save the service ID and name in context.

### Step 2: Create First Client
- Post the first client to `/platform/v1/clients` with `source_name: automation`.
- Save ID, full name, and email in context.

### Step 3: Verify Empty Recently Active Widget
- Fetch `/business/search/v1/views`.
- Find the system clients view whose name contains recent activity wording.
- Store the view UID in `localStorage["clients-widget-selected-view"]` so the POV dashboard Clients widget opens the recently active view.
- Open `/app/dashboard` using the current app host.
- Prefer the current POV dashboard widget using `.clients-widget` and `[data-qa="VcEmptyState"]`.
- If the legacy `.dashboard-clients-container` is present, use the legacy assertion path.
- Verify the widget contains the visible empty state.

### Step 4: Create First Appointment
- Post to `/business/scheduling/v1/bookings` with the service ID, first staff ID, first client ID, and a future start time.
- Save the booking response in context.

### Step 5: Verify First Client
- Reload the dashboard.
- Poll the recently active widget until the visible client names equal `[first_client["name"]]`.
- Reload during polling because seeker indexing can lag.

### Step 6: Create Second Client And Appointment
- Create the second client through `/platform/v1/clients`.
- Create the second appointment through `/business/scheduling/v1/bookings`.

### Step 7: Verify Client Ordering
- Reload the dashboard.
- Poll the recently active widget until the visible client names equal `[second_client["name"], first_client["name"]]`.

## Selectors
- Preferred stable selectors on the current dashboard: `[data-qa="VcSelectField"]`, `[data-qa="VcEmptyState"]`, and `[data-qa="VcClientItem"]`.
- Fallback selector for the legacy dashboard: `.dashboard-clients-container`, matching the legacy page object.
- Legacy client name selector: `.dashboard-clients-container div.list-item div.list-item-text div.title-md`.
- Legacy empty state selector: `.dashboard-clients-container .empty-state:not(.ng-hide)`.

## Success Verification
- Empty-state assertion passes before appointments.
- One-client assertion passes after the first appointment.
- Two-client ordered assertion passes after the second appointment.
