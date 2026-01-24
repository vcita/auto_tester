# Scheduling Module Test Plan

## Overview

This document defines the comprehensive test plan for vcita's Scheduling module from the **business (admin) side**. This covers appointment scheduling, calendar management, and booking configuration.

**Scope**: Business admin functionality only (not client-side booking)

**Status**: In Progress - Services, Appointments, and Events Implemented

---

## 1. Research Summary

### Module Features Discovered

**Core Scheduling Features:**
- Services (1-on-1 appointments) - CRUD operations
- Group Events (multi-participant sessions) - CRUD operations
- Manual appointment creation by business
- Calendar view and management
- Working hours configuration
- Booking settings (buffer time, advance booking limits)

**Calendar Integration:**
- Google Calendar sync (2-way)
- Outlook/Apple Calendar sync
- External calendar availability blocking

**Staff Management (if applicable):**
- Staff calendars
- Service assignment per staff
- Individual working hours

**Booking Configuration:**
- Online booking widget settings
- Booking page customization
- Confirmation and reminder settings

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
│   ├── remove_attendee/       # ⚠️ Partial (needs UI exploration fix)
│   ├── edit_event/            # ✅ Done
│   └── cancel_event/          # ✅ Done
│
├── calendar/                  # 🆕 NEW - Calendar management
│   ├── _category.yaml
│   ├── set_working_hours/     # Configure business hours
│   ├── block_time/            # Block time slots (vacation, breaks)
│   ├── view_day/              # Navigate calendar day view
│   ├── view_week/             # Navigate calendar week view
│   └── view_month/            # Navigate calendar month view
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
| 4 | remove_attendee | Remove Attendee | medium | ⚠️ Partial | Remove a client from the event (needs UI exploration fix) |
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

| Order | Test ID | Name | Priority | Description |
|-------|---------|------|----------|-------------|
| 1 | view_calendar_day | View Day | medium | Navigate to day view and verify |
| 2 | view_calendar_week | View Week | medium | Navigate to week view and verify |
| 3 | view_calendar_month | View Month | medium | Navigate to month view and verify |
| 4 | set_working_hours | Set Working Hours | high | Configure business working hours |
| 5 | block_time | Block Time | medium | Create a time block (vacation/break) |
| 6 | unblock_time | Unblock Time | medium | Remove time block |

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
- `blocked_time_id`

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
3. ✅ **Events subcategory** - 6 of 7 tests implemented (remove_attendee needs UI exploration fix)

**Events Implementation Notes:**
- `_setup` - Creates group event service and test client ✅
- `schedule_event` - Schedules event (uses default date if date picker doesn't appear) ✅
- `view_event` - Views event details (handles already being on event page) ✅
- `add_attendee` - Adds client to event ✅
- `remove_attendee` - Needs UI exploration to find correct remove button interaction ⚠️
- `edit_event` - Modifies event max attendance ✅
- `cancel_event` - Cancels scheduled event ✅

**Known Issues:**
- `schedule_event`: Date picker menu sometimes doesn't appear - test falls back to default date
- `remove_attendee`: Remove button interaction needs further UI exploration

### 🔜 Next: Calendar Subcategory (Medium Priority)

**Implementation Tasks:**
1. Create `calendar/_category.yaml` with subcategory configuration
2. Implement tests in order:
   - `view_calendar_day` - Navigate to day view and verify
   - `view_calendar_week` - Navigate to week view and verify
   - `view_calendar_month` - Navigate to month view and verify
   - `set_working_hours` - Configure business working hours
   - `block_time` - Create a time block (vacation/break)
   - `unblock_time` - Remove time block

**Prerequisites:**
- User is logged in
- Calendar page is accessible

**Context Variables to Save:**
- `working_hours_set` - Boolean flag indicating working hours configured
- `blocked_time_id` - ID of created time block

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
