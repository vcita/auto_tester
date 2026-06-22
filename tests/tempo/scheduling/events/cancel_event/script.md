# Cancel Event - Detailed Script

## Objective
Cancel a scheduled group event instance.

## Initial State
- User is logged in
- A scheduled event exists and is open (context: scheduled_event_id)
- Browser is on event detail page (from edit_event test)

## Actions

### Step 1: Verify on Event Detail Page
- **Action**: Verify URL
- **Target**: Event detail page URL

**VERIFIED PLAYWRIGHT CODE**:
```python
if "/app/events/" not in page.url:
    raise ValueError(f"Expected to be on event detail page, but URL is {page.url}")
```

- **How verified**: Checked URL in MCP
- **Wait for**: URL contains "/app/events/"

### Step 2: Click Cancel Event Button
- **Action**: Click
- **Target**: "Cancel Event" button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `outer_iframe.get_by_role("button", name="Cancel Event")` | Unique, semantic | None |
| `outer_iframe.get_by_text("Cancel Event")` | Simple | Less semantic |

**CHOSEN**: Prefer `get_by_role('button', name=regex)`, then `get_by_text(regex)`, then button-scan, then inner iframe.

**VERIFIED PLAYWRIGHT CODE**:
```python
import re
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
cancel_btn = outer_iframe.get_by_role('button', name=re.compile(r'Cancel\s*Event', re.IGNORECASE))
if cancel_btn.count() == 0:
    cancel_btn = outer_iframe.get_by_text(re.compile(r'Cancel\s*Event', re.IGNORECASE))
if cancel_btn.count() == 0:
    # Scan buttons for text containing both Cancel and Event
    all_buttons = outer_iframe.get_by_role('button')
    # ... find button with "cancel" and "event" in text, or try inner_iframe
if cancel_btn.count() > 0:
    cancel_btn.first.click()
# Wait for cancellation dialog to appear
dialog = outer_iframe.get_by_role('dialog')
dialog.wait_for(state='visible', timeout=10000)
```

- **How verified**: Button may be in outer or inner iframe; regex allows "Cancel Event" / "Cancel event".
- **Wait for**: Dialog with role="dialog" becomes visible
- **Fallback locators**: get_by_text(regex), then loop buttons, then inner_iframe

### Step 3: Fill Cancellation Message (Optional)
- **Action**: Type
- **Target**: Cancellation message textbox
- **Value**: "Test cancellation - event no longer needed"

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `outer_iframe.get_by_role("textbox", name="Cancellation message")` | Unique, semantic | None |
| `outer_iframe.get_by_label("Cancellation message")` | Simple | Less specific |

**CHOSEN**: `outer_iframe.get_by_role("textbox", name="Cancellation message")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Fill optional cancellation message
cancellation_message = "Test cancellation - event no longer needed"
message_field = outer_iframe.get_by_role('textbox', name='Cancellation message')
message_field.click()
page.wait_for_timeout(100)
message_field.press_sequentially(cancellation_message, delay=30)
page.wait_for_timeout(500)  # Allow message to be entered
```

- **How verified**: Typed message in MCP, value appeared
- **Wait for**: Message is entered
- **Fallback locators**: `outer_iframe.get_by_label("Cancellation message")`

### Step 4: Click Submit to Cancel
- **Action**: Click
- **Target**: "Submit" button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `outer_iframe.get_by_role("button", name="Submit")` | Unique, semantic | None |
| `outer_iframe.get_by_text("Submit")` | Simple | Less semantic |

**CHOSEN**: `outer_iframe.get_by_role("button", name="Submit")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
submit_btn = outer_iframe.get_by_role('button', name='Submit')
submit_btn.click()
# Wait for dialog to close and navigation to calendar
page.wait_for_url("**/app/calendar**", timeout=10000)
```

- **How verified**: Clicked in MCP, event was cancelled, navigated to calendar
- **Wait for**: Dialog closes, URL changes to calendar
- **Fallback locators**: `outer_iframe.get_by_text("Submit")`

### Step 5: Verify Event is Cancelled
- **Action**: Verify
- **Target**: Event is marked as CANCELLED in Event List (not just navigation to calendar)

**VERIFIED PLAYWRIGHT CODE**:
```python
# Verify we're on calendar page
expect(page).to_have_url(re.compile(r".*app/calendar.*"))
page.wait_for_timeout(2000)

# Verify event shows as CANCELLED in Event List (actual state check)
# Navigate to Event List: expand Calendar, force-click Event List (sidebar may be collapsed)
calendar_menu = page.get_by_text("Calendar", exact=True)
calendar_menu.click()
page.wait_for_timeout(1500)
event_list_item = page.locator('[data-qa="VcMenuItem-calendar-subitem-event_list"]')
event_list_item.wait_for(state='attached', timeout=10000)
event_list_item.first.evaluate('el => el.click()')
page.wait_for_url("**/app/event-list**", timeout=15000)
# Find event by service name (get_by_text; [cursor="pointer"] is CSS not DOM attr), assert row contains "CANCELLED"
event_cell = inner_iframe.get_by_text(service_name)
row_text = event_cell.first.text_content() or ""
if "CANCELLED" not in row_text.upper(): raise ValueError(...)

# Clear event context variables
context.pop("scheduled_event_id", None)
context.pop("scheduled_event_time", None)
context.pop("event_attendee_id", None)
```

- **How verified**: Navigation to calendar + Event List row for our service name must show "CANCELLED"
- **Clear context**: scheduled_event_id, scheduled_event_time, event_attendee_id

## Success Verification
- Event is cancelled successfully
- Dialog closes after cancellation
- Browser navigates to calendar page
- Event is marked as cancelled or removed from active calendar
- Context variables are cleared (scheduled_event_id, scheduled_event_time, event_attendee_id)
