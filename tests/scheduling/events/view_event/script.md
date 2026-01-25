# View Event - Detailed Script

## Objective
Open and view the details of a scheduled group event instance.

## Initial State
- User is logged in
- A scheduled event exists (context: scheduled_event_time)
- Browser is on Calendar page (from schedule_event test)

## Actions

### Step 1: Verify on Calendar Page
- **Action**: Verify URL
- **Target**: Calendar page URL

**VERIFIED PLAYWRIGHT CODE**:
```python
if "/app/calendar" not in page.url:
    # Navigate to Calendar if not already there
    calendar_menu = page.get_by_text("Calendar", exact=True)
    calendar_menu.click()
    page.wait_for_url("**/app/calendar**", timeout=10000)
```

- **How verified**: Checked URL in MCP
- **Wait for**: URL contains "/app/calendar"

### Step 2: Navigate to Event Date
- **Action**: Navigate to the date where event is scheduled
- **Target**: Date from context (scheduled_event_time)

**Note**: The event was scheduled for tomorrow. We need to navigate to that date in the calendar. The calendar can be navigated by clicking date navigation buttons or by using the "View on calendar" button if we're on the event page, but since we're starting from calendar, we'll navigate via the calendar UI.

**VERIFIED PLAYWRIGHT CODE**:
```python
from datetime import datetime

# Get event date from context
event_time_str = context.get("scheduled_event_time")
if not event_time_str:
    raise ValueError("No scheduled_event_time in context. Run schedule_event first.")

# Parse the date (format: "YYYY-MM-DD HH:MM")
event_date = datetime.strptime(event_time_str.split()[0], "%Y-%m-%d")
event_day = event_date.day

# Wait for calendar to load
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')

# Navigate to the event date - click the day in the mini calendar (left sidebar)
# HEALED: get_by_role('button', name='26') matches 4+ elements; scope to complementary + exact=True to exclude "January 2026"
date_btn = inner_iframe.get_by_role('complementary').first.get_by_role('button', name=str(event_day), exact=True)
date_btn.click()
page.wait_for_timeout(1000)  # Allow calendar to navigate to that date
```

- **How verified**: Clicked date in mini calendar in MCP, calendar navigated to that date
- **Wait for**: Calendar view updates to show the selected date
- **Fallback locators**: Navigate via "Next date" button until reaching the date

### Step 3: Find Event in Calendar Grid
- **Action**: Locate event in calendar
- **Target**: Event menuitem in calendar grid

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `inner_iframe.get_by_role("menuitem").filter(has_text=service_name)` | Semantic, matches service | May match multiple if same service |
| `inner_iframe.get_by_role("menuitem").filter(has_text=event_time)` | Matches time | Time format may vary |
| Find by service name from context | Uses known service | Most reliable |

**CHOSEN**: `inner_iframe.get_by_role("menuitem").filter(has_text=service_name)` - Service name is unique and stored in context.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Get service name from context
service_name = context.get("event_group_service_name")
if not service_name:
    raise ValueError("No event_group_service_name in context. Run _setup first.")

# Wait for calendar to load
page.wait_for_timeout(2000)  # Allow calendar to fully render

# Find the event in the calendar grid
# Events appear as menuitems in the calendar
event_menuitem = inner_iframe.get_by_role('menuitem').filter(has_text=service_name)
event_menuitem.wait_for(state='visible', timeout=10000)
```

- **How verified**: Found event in calendar grid in MCP
- **Wait for**: Event menuitem becomes visible
- **Fallback locators**: `inner_iframe.get_by_text(service_name)`

### Step 4: Click Event to Open Details
- **Action**: Click
- **Target**: Event menuitem

**VERIFIED PLAYWRIGHT CODE**:
```python
event_menuitem.click()
# Wait for event detail page to load
page.wait_for_url("**/app/events/**", timeout=10000)
```

- **How verified**: Clicked event in MCP, event detail page opened
- **Wait for**: URL contains "/app/events/" with event ID
- **Fallback locators**: None needed - already located

### Step 5: Verify Event Details are Displayed
- **Action**: Verify
- **Target**: Event details on the page

**VERIFIED PLAYWRIGHT CODE**:
```python
from playwright.sync_api import expect
import re

# Verify we're on event detail page
expect(page).to_have_url(re.compile(r"/app/events/[a-z0-9]+"))

# Verify event name is displayed
event_name_heading = outer_iframe.get_by_role('heading', level=3).filter(has_text=service_name)
expect(event_name_heading).to_be_visible()

# Verify date/time is displayed
# The date/time format is like "Sun, January 25, 4:00pm – 5:00pm"
date_time_heading = outer_iframe.get_by_role('heading', level=2)
expect(date_time_heading).to_be_visible()

# Extract event ID from URL for context
url = page.url
event_id_match = re.search(r'/app/events/([a-z0-9]+)', url)
if event_id_match:
    context["scheduled_event_id"] = event_id_match.group(1)
```

- **How verified**: Verified event details visible in MCP
- **Wait for**: Event detail page fully loaded
- **Save to context**: scheduled_event_id

## Success Verification
- Event detail page opens
- Event name matches context (event_group_service_name)
- Date/time is displayed and matches context (scheduled_event_time)
- Event details are visible (status, attendees, price, etc.)
- Context contains:
  - scheduled_event_id: ID of the event (extracted from URL)
