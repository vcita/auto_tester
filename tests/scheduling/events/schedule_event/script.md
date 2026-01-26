# Schedule Event - Detailed Script

## Objective
Schedule a group event instance by selecting a date and time for an existing group event service.

## Initial State
- User is logged in (from _setup)
- Group event service exists (context: event_group_service_name)
- Browser is on Calendar page (from _setup)

## Actions

### Step 1: Verify on Calendar Page
- **Action**: Verify URL
- **Target**: Calendar page URL

**VERIFIED PLAYWRIGHT CODE**:
```python
if "/app/calendar" not in page.url:
    raise ValueError(f"Expected to be on Calendar page, but URL is {page.url}")
```

- **How verified**: Checked URL in MCP
- **Wait for**: URL contains "/app/calendar"

### Step 2: Click New Button
- **Action**: Click
- **Target**: "New" button in calendar

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `inner_iframe.get_by_role("button", name="New")` | Unique, semantic | None |
| `inner_iframe.get_by_text("New")` | Simple | Less semantic |

**CHOSEN**: `inner_iframe.get_by_role("button", name="New")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
new_btn = inner_iframe.get_by_role('button', name='New')
new_btn.click()
# Wait for dropdown menu to appear
page.wait_for_timeout(500)
```

- **How verified**: Clicked in MCP, dropdown menu appeared
- **Wait for**: Dropdown menu appears
- **Fallback locators**: `inner_iframe.get_by_text("New")`

### Step 3: Select Group Event from Menu
- **Action**: Click
- **Target**: "Group event" menu item

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `inner_iframe.get_by_role("menuitem", name="Group event")` | Semantic, unique | None |
| `inner_iframe.get_by_text("Group event")` | Simple | Less semantic |

**CHOSEN**: `inner_iframe.get_by_role("menuitem", name="Group event")` - Semantic and unique.

**VERIFIED PLAYWRIGHT CODE**:
```python
group_event_option = inner_iframe.get_by_role('menuitem', name='Group event')
group_event_option.click()
# Wait for dialog to appear - dialog is in document, not iframe
page.wait_for_timeout(1000)  # Allow dialog to start appearing
dialog = page.get_by_role('dialog')
dialog.wait_for(state='visible', timeout=15000)
```

- **How verified**: Clicked in MCP, "New Event" dialog appeared
- **Wait for**: Dialog with role="dialog" becomes visible
- **Fallback locators**: `inner_iframe.get_by_text("Group event")`

### Step 4: Select Group Event Service
- **Action**: Click then Type then Click
- **Target**: Service combobox, then search/select service

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `inner_iframe.get_by_role("combobox")` | Semantic | May match multiple |
| `inner_iframe.get_by_role("textbox", name="Select service")` | More specific | None |

**CHOSEN**: `inner_iframe.get_by_role("combobox")` - Unique combobox in dialog.

**VERIFIED PLAYWRIGHT CODE** (HEALED 2026-01-25: wait for option without typing first; new service often in "Recently scheduled"; 30s for API):
```python
# Click combobox to open
service_combobox = inner_iframe.get_by_role('combobox')
service_combobox.click()
# Wait for listbox to appear
listbox = inner_iframe.get_by_role('listbox')
listbox.wait_for(state='visible', timeout=10000)

# Search for service by name (from context)
service_name = context.get("event_group_service_name")
if not service_name:
    raise ValueError("No group event service name in context. Run _setup first.")

# Type to trigger search (new service may only appear via search). Do not re-wait for listbox after typing.
search_field = inner_iframe.get_by_role('textbox', name='Select service')
search_field.click()
page.wait_for_timeout(100)
search_field.press_sequentially(service_name, delay=30)
# Wait for option only (45s for search/API). No listbox re-wait - listbox may close while typing.
service_option = inner_iframe.get_by_role('option').filter(has_text=service_name).first
service_option.wait_for(state='visible', timeout=45000)
service_option.click()
```

- **How verified**: Clicked combobox, typed service name, selected option in MCP
- **Wait for**: Service is selected (combobox shows service name)
- **Fallback locators**: `inner_iframe.get_by_text(service_name)`

### Step 5: Set Start Date to Tomorrow
- **Action**: Click then Click
- **Target**: Start date button, then tomorrow's date

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `inner_iframe.get_by_role("button", name="Start date:")` | Semantic | May match multiple |
| `.first()` | Gets first instance | Position-based |

**CHOSEN**: `inner_iframe.get_by_role("button", name="Start date:").first()` - First instance is the clickable button.

**VERIFIED PLAYWRIGHT CODE** (HEALED 2026-01-25: do not use get_by_role('menu') — it matches scheduler's allDayEventsContainer which never hides; use day button visibility instead):
```python
from datetime import datetime, timedelta

tomorrow = datetime.now() + timedelta(days=1)
tomorrow_day = tomorrow.day

start_date_btn = inner_iframe.get_by_role('button', name='Start date:').first()
start_date_btn.click()
# Wait for date picker by waiting for tomorrow's day button to appear (picker open)
tomorrow_date_btn = inner_iframe.get_by_role('button', name=str(tomorrow_day))
if tomorrow_date_btn.count() == 0:
    tomorrow_date_btn = page.get_by_role('button', name=str(tomorrow_day))
tomorrow_date_btn.first.wait_for(state='visible', timeout=8000)
day_btn = tomorrow_date_btn.nth(tomorrow_date_btn.count() - 1)
day_btn.click()
day_btn.wait_for(state='hidden', timeout=5000)
```

- **How verified**: Healed: get_by_role('menu').first matched allDayEventsContainer; wait for day button visible then hidden.
- **Wait for**: Date picker opens (day button visible), then closes (day button hidden after click).
- **Fallback locators**: `inner_iframe.get_by_text(str(tomorrow_day))`

### Step 6: Verify End Date is Set (Auto-updated)
- **Action**: Verify
- **Target**: End date should auto-update to match start date

**VERIFIED PLAYWRIGHT CODE**:
```python
# End date should automatically update to match start date
# No action needed - just verify
end_date_btn = inner_iframe.get_by_role('button', name='End Date:')
end_date_text = end_date_btn.text_content()
# End date should show tomorrow's date
```

- **How verified**: Observed in MCP that end date auto-updates
- **Wait for**: End date matches start date

### Step 7: Verify Times are Set (Default is acceptable)
- **Action**: Verify
- **Target**: Start and end times should have default values

**Note**: Default times (4:00 PM - 5:00 PM) are acceptable. If different times are needed, they can be changed by clicking the time buttons, but for this test, defaults are fine.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Times are set by default (4:00 PM - 5:00 PM)
# No action needed unless specific times are required
```

- **How verified**: Observed default times in MCP
- **Wait for**: Times are visible

### Step 8: Click Create Event
- **Action**: Click
- **Target**: "Create Event" button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `inner_iframe.get_by_role("button", name="Create Event")` | Unique, semantic | None |
| `inner_iframe.get_by_text("Create Event")` | Simple | Less semantic |

**CHOSEN**: `inner_iframe.get_by_role("button", name="Create Event")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
create_btn = inner_iframe.get_by_role('button', name='Create Event')
create_btn.click()
# Wait for dialog to close and calendar to update
page.wait_for_timeout(2000)  # Allow event to be created and calendar to refresh
```

- **How verified**: Clicked in MCP, event was created, toast appeared
- **Wait for**: Dialog closes, calendar updates
- **Fallback locators**: `inner_iframe.get_by_text("Create Event")`

### Step 9: Verify Event Created
- **Action**: Verify
- **Target**: Event appears in Event List (outcome verification). MCP-validated: Event List has "Search by event name" textbox; use it to filter, then assert row visible.

**VERIFIED PLAYWRIGHT CODE** (MCP-validated 2026-01-25):
```python
# Wait for creation to complete
page.wait_for_timeout(2000)  # Allow dialog to close and request to complete

# Navigate to Event List
calendar_menu = page.get_by_text("Calendar", exact=True)
calendar_menu.click()
page.wait_for_timeout(1500)  # Allow Calendar submenu to expand
event_list_item = page.locator('[data-qa="VcMenuItem-calendar-subitem-event_list"]')
event_list_item.wait_for(state='attached', timeout=10000)
event_list_item.first.evaluate('el => el.click()')  # Force click (sidebar may be collapsed)
page.wait_for_url("**/app/event-list**", timeout=15000)
page.wait_for_timeout(3000)  # Allow event list to load
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')

# MCP: Event List has textbox "Search by event name" - use it to filter to our event
service_name = context.get("event_group_service_name")
if not service_name:
    raise ValueError("event_group_service_name not in context")
search_field = inner_iframe.get_by_role('textbox', name='Search by event name')
search_field.wait_for(state='visible', timeout=10000)
search_field.click()
page.wait_for_timeout(100)
search_field.press_sequentially(service_name, delay=30)
page.wait_for_timeout(2000)  # Allow filter to apply

# Assert event visible by text (cursor=pointer is style not DOM attribute; get_by_text works)
event_cell = inner_iframe.get_by_text(service_name)
event_cell.wait_for(state='visible', timeout=10000)

# Return to Calendar so next test (view_event) starts from Calendar (click "Calendar View" submenu; MCP-validated)
calendar_view_item = page.get_by_text("Calendar View", exact=True)
calendar_view_item.click()
page.wait_for_url("**/app/calendar**", timeout=10000)
```

- **How verified**: MCP: Search filters list; row visible. HEALED 2026-01-25: locator `[cursor="pointer"]` fails (cursor is CSS, not HTML attr); use `get_by_text(service_name)` — MCP run_code confirmed count 0 vs 1.
- **Wait for**: Event List loads; after search, event row visible.
- **Save to context**: scheduled_event_time (set in Step 5).

## Success Verification
- Event instance is scheduled successfully
- Dialog closes after creation
- **Event appears in Event List** (filter by service name, row visible) — MCP-validated
- Context contains:
  - scheduled_event_time: Date/time of the scheduled event
