# Scheduling Module Test Plan

## Overview

This document defines the comprehensive test plan for vcita's Scheduling module from the **business (admin) side**. This covers appointment scheduling, calendar management, and booking configuration.

**Scope**: Business admin functionality only (not client-side booking)

**Status**: In Progress - Services, Appointments, and Events Implemented | Calendar Subcategory Planned

---

## 1. Research Summary

### Module Features Discovered

**Core Scheduling Features:**
- Services (1-on-1 appointments) - CRUD operations ✅
- Group Events (multi-participant sessions) - CRUD operations ✅
- Manual appointment creation by business ✅
- Calendar view and management (Day, 3 Days, Week, Month, Agenda views) 🆕
- Working hours configuration (per day, multiple time slots, date-specific) 🆕
- Calendar navigation (Previous/Next/Today buttons) 🆕
- Calendar list views (Appointment List, Event List) 🆕
- Booking settings (buffer time, advance booking limits)

**Calendar Integration:**
- Google Calendar sync (2-way) - Settings > Availability & Calendar > Calendar sync
- Outlook/Apple Calendar sync - Settings > Availability & Calendar > Calendar sync
- External calendar availability blocking
- "Connect an external calendar" option in calendar sidebar 🆕

**Staff Management (if applicable):**
- Staff calendars
- Service assignment per staff
- Individual working hours

**Booking Configuration:**
- Online booking widget settings
- Booking page customization
- Confirmation and reminder settings

**Calendar Business Settings (Discovered via MCP):**
- Start week on (Sunday/Monday/etc.) - Settings > Availability & Calendar > Business settings
- Time format (12-hour AM/PM or 24-hour) - Settings > Availability & Calendar > Business settings
- Time zone configuration - Settings > Availability & Calendar > General availability
- Local business time zone display option 🆕

**Calendar Actions (Discovered via MCP):**
- Invite to schedule (from More actions menu)
- Print calendar (from More actions menu)
- Export booking data (from More actions menu)
- View reports (from More actions menu)

---

## 2. Category Structure

```
scheduling/
├── _setup/                    # Login + navigate to calendar/scheduling area
├── _category.yaml             # Main category config
│
├── services/                  # ✅ IMPLEMENTED
│   ├── _category.yaml
│   ├── create_service/        # ✅ Done
│   ├── edit_service/          # ✅ Done
│   ├── delete_service/        # ✅ Done
│   ├── create_group_event/    # ✅ Done
│   ├── edit_group_event/      # ✅ Done
│   └── delete_group_event/    # ✅ Done
│
├── appointments/              # ✅ IMPLEMENTED
│   ├── _category.yaml
│   ├── _setup/                # ✅ Done
│   ├── _teardown/             # ✅ Done
│   ├── create_appointment/    # ✅ Done
│   ├── create_custom_appointment/ # ✅ Done
│   ├── view_appointment/      # ✅ Done
│   ├── edit_appointment/      # ✅ Done
│   ├── reschedule_appointment/# ✅ Done
│   ├── cancel_appointment/    # ✅ Done
│   └── cancel_custom_appointment/ # ✅ Done
│
├── events/                    # ✅ IMPLEMENTED
│   ├── _category.yaml
│   ├── _setup/                # ✅ Done
│   ├── schedule_event/        # ✅ Done
│   ├── view_event/              # ✅ Done
│   ├── add_attendee/          # ✅ Done
│   ├── remove_attendee/       # ✅ Done
│   ├── edit_event/            # ✅ Done
│   └── cancel_event/          # ✅ Done
│
├── calendar/                  # 🆕 NEW - Calendar management
│   ├── _category.yaml
│   ├── view_calendar_day/     # Navigate to day view
│   ├── view_calendar_3days/   # Navigate to 3-day view
│   ├── view_calendar_week/    # Navigate to week view
│   ├── view_calendar_month/   # Navigate to month view
│   ├── view_calendar_agenda/  # Navigate to agenda view
│   ├── navigate_calendar_previous/ # Navigate to previous date
│   ├── navigate_calendar_next/   # Navigate to next date
│   ├── navigate_calendar_today/   # Navigate to today
│   ├── view_appointment_list/ # Switch to appointment list view
│   ├── view_event_list/       # Switch to event list view
│   ├── set_working_hours/     # Configure business working hours
│   ├── set_multiple_time_slots/ # Add multiple time slots per day
│   ├── toggle_day_availability/ # Toggle day on/off
│   ├── edit_time_slot/        # Edit existing time slot
│   ├── delete_time_slot/      # Delete time slot
│   ├── set_date_specific_availability/ # Configure specific date availability
│   ├── block_date/            # Block a specific date
│   ├── unblock_date/          # Remove date block
│   ├── set_start_week_on/     # Configure week start day
│   ├── set_time_format/       # Set 12/24 hour format
│   ├── set_time_zone/         # Configure time zone
│   ├── calendar_invite_to_schedule/ # Invite to schedule action
│   ├── calendar_print/        # Print calendar
│   ├── calendar_export_data/  # Export booking data
│   └── calendar_view_reports/ # View reports
│
└── booking_settings/          # 🆕 NEW - Booking configuration (lower priority)
    ├── _category.yaml
    ├── set_advance_booking/   # How far in advance clients can book
    ├── set_buffer_time/       # Time between appointments
    └── set_cancellation_policy/ # Cancellation rules
```

---

## 3. Test Lists by Subcategory

### 3.1 Services Subcategory (✅ IMPLEMENTED)

| Order | Test ID | Name | Priority | Status | Description |
|-------|---------|------|----------|--------|-------------|
| 1 | create_service | Create Service | high | ✅ Done | Create 1-on-1 service |
| 2 | edit_service | Edit Service | high | ✅ Done | Modify service details |
| 3 | delete_service | Delete Service | high | ✅ Done | Delete test service |
| 4 | create_group_event | Create Group Event | high | ✅ Done | Create group event service |
| 5 | edit_group_event | Edit Group Event | high | ✅ Done | Modify group event |
| 6 | delete_group_event | Delete Group Event | high | ✅ Done | Delete test group event |

### 3.2 Appointments Subcategory (✅ IMPLEMENTED)

| Order | Test ID | Name | Priority | Status | Description |
|-------|---------|------|----------|--------|-------------|
| 0 | _setup | Setup | high | ✅ Done | Create test service and client for appointments |
| 1 | create_appointment | Create Appointment | high | ✅ Done | Manually create a 1-on-1 appointment for existing client |
| 2 | view_appointment | View Appointment | high | ✅ Done | Open and view appointment details |
| 3 | edit_appointment | Edit Appointment | high | ✅ Done | Change appointment notes, service, or other details |
| 4 | reschedule_appointment | Reschedule Appointment | high | ✅ Done | Change appointment date/time |
| 5 | cancel_appointment | Cancel Appointment | high | ✅ Done | Cancel the appointment (mark as cancelled) |
| 6 | create_custom_appointment | Create Custom Appointment | medium | ✅ Done | Create an appointment without using a predefined service |
| 7 | cancel_custom_appointment | Cancel Custom Appointment | high | ✅ Done | Cancel the custom appointment |
| 8 | _teardown | Teardown | high | ✅ Done | Clean up test data |

**Context Flow:**
- create_appointment → saves: `created_appointment_id`, `created_appointment_time`
- All subsequent tests read from context
- cancel/delete → clears context

### 3.3 Events Subcategory (✅ IMPLEMENTED)

| Order | Test ID | Name | Priority | Status | Description |
|-------|---------|------|----------|--------|-------------|
| 0 | _setup | Setup | high | ✅ Done | Create group event service and test client for event scheduling |
| 1 | schedule_event | Schedule Event | high | ✅ Done | Schedule a group event instance (select date/time) |
| 2 | view_event | View Event | high | ✅ Done | Open and view event details |
| 3 | add_attendee | Add Attendee | high | ✅ Done | Add a client to the event |
| 4 | remove_attendee | Remove Attendee | medium | ✅ Done | Remove a client from the event |
| 5 | edit_event | Edit Event | high | ✅ Done | Modify event details |
| 6 | cancel_event | Cancel Event | high | ✅ Done | Cancel the scheduled event |

**Prerequisites:**
- Requires a group event service to exist (from services subcategory)
- Requires at least one client to exist (from clients category)

**Context Flow:**
- schedule_event → saves: `scheduled_event_id`, `scheduled_event_time`
- add_attendee → saves: `event_attendee_id`
- cancel_event → clears context

### 3.4 Calendar Subcategory (🆕 NEW - Medium Priority)

**Calendar Features Discovered via MCP Exploration:**
- Calendar views: Day, 3 Days, Week, Month, Agenda
- Calendar navigation: Previous/Next date, Today button
- Calendar list views: Calendar View, Appointment List, Event List
- Working hours: Set per day, multiple time slots per day, toggle days on/off, edit/delete time slots
- Date-specific availability: Block specific dates or set different hours
- Business settings: Start week on, time format, time zone
- Calendar actions: Invite to schedule, Print, Export booking data, View reports

| Order | Test ID | Name | Priority | Status | Description |
|-------|---------|------|----------|--------|-------------|
| 1 | view_calendar_day | View Day | medium | ⏳ Pending | Navigate to day view and verify calendar displays correctly |
| 2 | view_calendar_3days | View 3 Days | medium | ⏳ Pending | Navigate to 3-day view and verify calendar displays correctly |
| 3 | view_calendar_week | View Week | medium | ⏳ Pending | Navigate to week view and verify calendar displays correctly |
| 4 | view_calendar_month | View Month | medium | ⏳ Pending | Navigate to month view and verify calendar displays correctly |
| 5 | view_calendar_agenda | View Agenda | low | ⏳ Pending | Navigate to agenda view and verify list displays correctly |
| 6 | navigate_calendar_previous | Navigate Previous Date | medium | ⏳ Pending | Click previous date button and verify calendar updates |
| 7 | navigate_calendar_next | Navigate Next Date | medium | ⏳ Pending | Click next date button and verify calendar updates |
| 8 | navigate_calendar_today | Navigate Today | medium | ⏳ Pending | Click today button and verify calendar shows current date |
| 9 | view_appointment_list | View Appointment List | medium | ⏳ Pending | Switch to appointment list view and verify appointments display |
| 10 | view_event_list | View Event List | medium | ⏳ Pending | Switch to event list view and verify events display |
| 11 | set_working_hours | Set Working Hours | high | ⏳ Pending | Configure business working hours for a day |
| 12 | set_multiple_time_slots | Set Multiple Time Slots | medium | ⏳ Pending | Add multiple time slots for a single day (e.g., 9-12 AM and 2-5 PM) |
| 13 | toggle_day_availability | Toggle Day Availability | medium | ⏳ Pending | Toggle a day on/off (enable/disable working hours) |
| 14 | edit_time_slot | Edit Time Slot | medium | ⏳ Pending | Modify an existing time slot (change start/end time) |
| 15 | delete_time_slot | Delete Time Slot | medium | ⏳ Pending | Remove a time slot from a day |
| 16 | set_date_specific_availability | Set Date-Specific Availability | medium | ⏳ Pending | Configure availability for a specific date (different from regular hours) |
| 17 | block_date | Block Date | medium | ⏳ Pending | Block a specific date (mark as unavailable) |
| 18 | unblock_date | Unblock Date | medium | ⏳ Pending | Remove a date block (restore to regular availability) |
| 19 | set_start_week_on | Set Start Week On | low | ⏳ Pending | Configure which day the week starts on (Sunday/Monday/etc.) |
| 20 | set_time_format | Set Time Format | low | ⏳ Pending | Change time format between 12-hour (AM/PM) and 24-hour |
| 21 | set_time_zone | Set Time Zone | medium | ⏳ Pending | Configure default time zone for calendar |
| 22 | calendar_invite_to_schedule | Invite to Schedule | low | ⏳ Pending | Use "Invite to schedule" action from calendar menu |
| 23 | calendar_print | Print Calendar | low | ⏳ Pending | Use print action from calendar menu |
| 24 | calendar_export_data | Export Booking Data | low | ⏳ Pending | Export booking data from calendar menu |
| 25 | calendar_view_reports | View Reports | low | ⏳ Pending | Access reports from calendar menu |

### 3.5 Booking Settings Subcategory (🆕 NEW - Low Priority)

| Order | Test ID | Name | Priority | Description |
|-------|---------|------|----------|-------------|
| 1 | view_booking_settings | View Settings | low | Navigate to booking settings |
| 2 | set_advance_booking | Set Advance Booking | low | Configure how far ahead clients can book |
| 3 | set_buffer_time | Set Buffer Time | low | Configure buffer between appointments |
| 4 | set_cancellation_policy | Set Cancellation Policy | low | Configure cancellation rules |

---

## 4. Execution Order

The subcategories should run in this order:

```
1. _setup (login, navigate to scheduling area)
   │
   ├── 2. services/ (create service types first)
   │      └── run_after: _setup
   │
   ├── 3. appointments/ (need services to create appointments)
   │      └── run_after: services/delete_service (after 1-on-1 service CRUD)
   │
   ├── 4. events/ (need group event service + client)
   │      └── run_after: services/delete_group_event (after group event CRUD)
   │
   ├── 5. calendar/ (independent, can run anytime after setup)
   │      └── run_after: events
   │
   └── 6. booking_settings/ (configuration, run last)
         └── run_after: calendar
```

**Note on Dependencies:**
- `appointments` tests need a 1-on-1 service to exist → Create one in appointments/_setup
- `events` tests need a group event service AND a client → Create in events/_setup
- This keeps subcategories independent and self-contained

---

## 5. Context Variables

### Services (existing)
- `created_service_id` / `created_service_name`
- `created_group_event_id` / `created_group_event_name`

### Appointments (new)
- `created_appointment_id`
- `created_appointment_time`
- `appointment_client_id` (may reference clients context)
- `appointment_service_id`

### Events (new)
- `scheduled_event_id`
- `scheduled_event_time`
- `event_attendee_id`
- `event_group_service_id`

### Calendar (new)
- `working_hours_set` (boolean flag)
- `blocked_time_id` / `blocked_date`
- `time_slot_id` (for multiple time slots)
- `calendar_view_mode` (day/week/month/agenda)
- `calendar_current_date` (for navigation tests)

---

## 6. Implementation Priority

### Phase 1: High Priority (Implement First)
1. ✅ Services - DONE
2. ✅ Appointments - DONE (Manual appointment CRUD)
3. ✅ Events - DONE (Group event scheduling - 6 of 7 tests complete)

### Phase 2: Medium Priority
4. 🔜 Calendar - Working hours and calendar navigation (NEXT)

### Phase 3: Low Priority
5. Booking Settings - Configuration options

---

## 7. Implementation Notes

### Special Considerations

1. **Time Sensitivity**: Appointment tests involve selecting dates/times. Use "tomorrow" or "next available slot" to avoid past-date issues.

2. **Client Dependency**: Some tests need an existing client. Options:
   - Run after clients category (complex dependency)
   - Create a test client in the subcategory _setup (self-contained)

3. **UI Navigation**: The vcita calendar UI uses iframes. Need careful MCP exploration.

4. **Event Capacity**: Group events have capacity limits. Tests should respect and verify these.

### Excluded from Initial Scope

- **Calendar sync tests** (Google, Outlook) - Requires external account setup
- **Multi-staff scheduling** - Requires team plan features
- **Client-side booking** - Different user context, separate test suite
- **Payment during booking** - Covered in payments module
- **Email notifications** - Hard to verify automatically

---

## 8. Next Steps

### ✅ Completed
1. ✅ **Services subcategory** - All 6 tests implemented
2. ✅ **Appointments subcategory** - All 7 tests + setup/teardown implemented
3. ✅ **Events subcategory** - All 6 tests implemented

**Events Implementation Notes:**
- `_setup` - Creates group event service and test client ✅
- `schedule_event` - Schedules event (uses default date if date picker doesn't appear) ✅
- `view_event` - Views event details (handles already being on event page) ✅
- `add_attendee` - Adds client to event (dialog-scoped locators, get_by_text fallback) ✅
- `remove_attendee` - Removes attendee via 3-dot menu / Cancel registration ✅
- `edit_event` - Modifies event max attendance; verifies "0/12 Registered" in outer iframe ✅
- `cancel_event` - Cancels scheduled event (flexible Cancel Event button locator) ✅

**Known Issues:**
- `schedule_event`: Date picker menu sometimes doesn't appear - test falls back to default date

### 🔜 Next: Calendar Subcategory (Medium Priority)

**Implementation Tasks:**
1. Create `calendar/_category.yaml` with subcategory configuration
2. Implement tests in priority order:

**High Priority:**
   - `set_working_hours` - Configure business working hours (core functionality)
   - `view_calendar_day` - Navigate to day view and verify
   - `view_calendar_week` - Navigate to week view and verify
   - `view_calendar_month` - Navigate to month view and verify

**Medium Priority:**
   - `navigate_calendar_today` - Navigate to today button
   - `navigate_calendar_previous` / `navigate_calendar_next` - Date navigation
   - `view_calendar_3days` - 3-day view
   - `view_appointment_list` / `view_event_list` - List views
   - `set_multiple_time_slots` - Multiple time slots per day
   - `toggle_day_availability` - Enable/disable days
   - `edit_time_slot` / `delete_time_slot` - Time slot management
   - `set_date_specific_availability` - Date-specific availability
   - `block_date` / `unblock_date` - Date blocking
   - `set_time_zone` - Time zone configuration

**Low Priority:**
   - `view_calendar_agenda` - Agenda view
   - `set_start_week_on` - Week start configuration
   - `set_time_format` - Time format (12/24 hour)
   - `calendar_invite_to_schedule` - Invite action
   - `calendar_print` - Print functionality
   - `calendar_export_data` - Export functionality
   - `calendar_view_reports` - Reports access

**Prerequisites:**
- User is logged in
- Calendar page is accessible (navigate to `/app/calendar`)
- Settings > Availability & Calendar page accessible for configuration tests

**Context Variables to Save:**
- `working_hours_set` - Boolean flag indicating working hours configured
- `blocked_time_id` / `blocked_date` - ID/date of created time block
- `time_slot_id` - ID of created time slot (for edit/delete tests)
- `calendar_view_mode` - Current view mode (day/week/month/agenda)
- `calendar_current_date` - Current date displayed in calendar

**Implementation Notes:**
- Calendar UI uses nested iframes: `iframe[title="angularjs"]` → `#vue_iframe_layout`
- View selector is a dropdown menu with options: Day, 3 Days, Week, Month, Agenda
- Working hours are configured in Settings > Availability & Calendar > General availability
- Date-specific availability uses "Edit date-specific availability" button
- Calendar actions are in "More actions" menu (top right of calendar)

### 📋 Future: Booking Settings Subcategory (Low Priority)
- Configuration options for booking rules
- Run after calendar subcategory

---

## Appendix: Test Details

### A1. Create Appointment Test

**Objective**: Manually create a 1-on-1 appointment from the business calendar

**Prerequisites**:
- Logged in as business admin
- At least one service exists
- At least one client exists

**Steps**:
1. Navigate to Calendar
2. Click "+" or "New Appointment" button
3. Select a client (search/select from list)
4. Select a service
5. Choose date and time
6. Add optional notes
7. Click Save/Create
8. Verify appointment appears in calendar

**Expected Result**:
- Appointment created successfully
- Appears in calendar at correct time
- Shows correct client and service

### A2. Schedule Event Test

**Objective**: Schedule an instance of a group event service

**Prerequisites**:
- Logged in as business admin
- A group event service exists
- At least one client exists (optional for initial scheduling)

**Steps**:
1. Navigate to Calendar or Events section
2. Click to schedule a group event
3. Select the group event service type
4. Choose date and time
5. Set capacity (if not using default)
6. Save the event
7. Verify event appears in calendar

**Expected Result**:
- Event instance created
- Shows on calendar with correct details
- Ready to accept attendees

---

## 9. MCP Exploration Summary (Calendar Features)

**Date**: January 27, 2026

**Exploration Method**: Used Playwright MCP browser tools to explore vcita calendar functionality

### Calendar Views Discovered:
1. **Day View** - Single day with hourly time slots (12 AM - 11 PM)
2. **3 Days View** - Three consecutive days displayed
3. **Week View** - Full week view
4. **Month View** - Full month calendar grid
5. **Agenda View** - List format of appointments/events

### Calendar Navigation:
- **Previous Date** button (left arrow) - Navigate to previous day/week/month
- **Next Date** button (right arrow) - Navigate to next day/week/month
- **Today** button - Jump to current date
- **Date picker** - Mini calendar in sidebar for quick date selection

### Calendar List Views (Sidebar):
- **Calendar View** - Main calendar grid view (default)
- **Appointment List** - List of all appointments
- **Event List** - List of all events

### Working Hours Configuration (Settings > Availability & Calendar > General availability):
- **Per-day toggles** - Enable/disable working hours for each day (Sunday-Saturday)
- **Time slots** - Set start and end time (e.g., 09:00 AM - 05:00 PM)
- **Multiple time slots** - "Add time slot" button allows multiple ranges per day
- **Edit/Delete time slots** - Edit (pencil icon) and delete (trash icon) buttons for each slot
- **Date-specific availability** - "Edit date-specific availability" button for specific dates

### Business Settings (Settings > Availability & Calendar > Business settings):
- **Start week on** - Dropdown: Sunday, Monday, etc.
- **Time format** - Dropdown: 12 hours (AM/PM) or 24 hours
- **Time zone** - Dropdown with timezone selection
- **Local business option** - Checkbox: "If your business is local, display all times for staff and clients in your time zone"

### Calendar Actions (More actions menu):
- **Invite to schedule** - Generate invite link
- **Print** - Print calendar view
- **Export booking data** - Export calendar data
- **View reports** - Access scheduling reports

### UI Structure:
- Calendar uses nested iframes:
  - Outer: `iframe[title="angularjs"]`
  - Inner: `#vue_iframe_layout` (Vue.js calendar component)
- View selector is a dropdown button showing current view (Day/Week/Month)
- Services list appears in left sidebar with checkboxes to filter calendar display
- Mini calendar appears in left sidebar for date navigation

### Key Locators Discovered:
- View selector: `button[name="Day"]` (or Week/Month) with dropdown menu
- More actions: `button[name="More actions"]`
- Today button: `button[name="Today"]`
- Previous/Next: Arrow buttons in calendar header
- Working hours: Settings > Availability & Calendar > General availability tab
- Time slot edit: Pencil icon button next to time range
- Time slot delete: Trash icon button next to time range
