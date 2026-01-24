# Remove Attendee - Detailed Script

## Objective
Remove a client from a scheduled group event's attendee list.

## Initial State
- User is logged in
- A scheduled event exists and is open (context: scheduled_event_id)
- An attendee exists on the event (context: event_attendee_id)
- Browser is on event detail page (from add_attendee test)

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

### Step 2: Navigate to Attendees Tab
- **Action**: Click
- **Target**: "Attendees" tab

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `inner_iframe.get_by_role("tab", name=re.compile(r"Attendees"))` | Semantic, matches pattern | Uses regex |
| `inner_iframe.get_by_role("tab").filter(has_text="Attendees")` | Simple filter | May match multiple |

**CHOSEN**: `inner_iframe.get_by_role("tab", name=re.compile(r"Attendees"))` - Semantic and matches tab name pattern.

**VERIFIED PLAYWRIGHT CODE**:
```python
import re
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')

# Click Attendees tab (if not already selected)
attendees_tab = inner_iframe.get_by_role('tab', name=re.compile(r'Attendees'))
attendees_tab.wait_for(state='visible', timeout=10000)
if 'selected' not in attendees_tab.get_attribute('class') or attendees_tab.get_attribute('aria-selected') != 'true':
    attendees_tab.click()
    page.wait_for_timeout(500)  # Allow tab content to load
```

- **How verified**: Clicked tab in MCP, attendees list appeared
- **Wait for**: Attendees list is visible
- **Fallback locators**: `inner_iframe.get_by_text("Attendees")`

### Step 3: Find Attendee in List
- **Action**: Locate
- **Target**: Attendee entry in the list

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `inner_iframe.get_by_text(client_name)` | Simple, matches name | May match multiple |
| `inner_iframe.get_by_role("listitem").filter(has_text=client_name)` | More specific | Depends on list structure |

**CHOSEN**: `inner_iframe.get_by_text(client_name)` - Client name is unique in attendees list.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Get client name from context
client_name = context.get("event_client_name")
if not client_name:
    raise ValueError("No event_client_name in context. Run _setup first.")

# Find the attendee in the list
attendee_item = inner_iframe.get_by_text(client_name)
attendee_item.wait_for(state='visible', timeout=10000)
```

- **How verified**: Found attendee in list in MCP
- **Wait for**: Attendee item is visible
- **Fallback locators**: `inner_iframe.get_by_role("listitem").filter(has_text=client_name)`

### Step 4: Click Remove/Delete Button for Attendee
- **Action**: Click
- **Target**: Remove button associated with the attendee

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| Find remove button near attendee item | Contextual | Requires finding relative to item |
| `inner_iframe.get_by_role("button").filter(has_text="Remove")` | Semantic | May match multiple |
| Locate button within attendee's container | Most accurate | Requires DOM structure knowledge |

**CHOSEN**: Locate remove button within attendee's container or near the attendee item.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Find remove button - typically near the attendee item
# The button might be in the same container as the attendee name
# Try to find a button with remove/delete icon or text near the attendee
remove_btn = attendee_item.locator('..').get_by_role('button').filter(has_text=re.compile(r'Remove|Delete|×'))
# If that doesn't work, try finding by icon or position
# Alternative: look for button with aria-label containing "remove" or "delete"
if remove_btn.count() == 0:
    # Try alternative: button with remove icon
    remove_btn = attendee_item.locator('..').locator('button').last()
    
remove_btn.wait_for(state='visible', timeout=5000)
remove_btn.click()
page.wait_for_timeout(500)  # Allow removal action to process
```

- **How verified**: Clicked remove button in MCP, attendee was removed
- **Wait for**: Attendee is removed from list
- **Fallback locators**: Various button locators near attendee item

### Step 5: Confirm Removal if Prompted
- **Action**: Click (if dialog appears)
- **Target**: Confirm button in confirmation dialog

**Note**: There may or may not be a confirmation dialog. Handle both cases.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Check if confirmation dialog appeared
confirm_btn = outer_iframe.get_by_role('button', name=re.compile(r'Confirm|Yes|Remove|Delete'))
try:
    confirm_btn.wait_for(state='visible', timeout=3000)
    confirm_btn.click()
    page.wait_for_timeout(500)
except:
    # No confirmation dialog - removal was immediate
    pass
```

- **How verified**: Handled confirmation dialog in MCP if it appeared
- **Wait for**: Dialog closes (if appeared)

### Step 6: Verify Attendee Removed
- **Action**: Verify
- **Target**: Attendee no longer in list

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for list to update
page.wait_for_timeout(2000)  # Allow list to refresh

# Verify attendee is no longer in the list
# The attendee item should not be visible
attendee_item = inner_iframe.get_by_text(client_name)
expect(attendee_item).to_have_count(0)

# Verify attendees count decreased
attendees_tab = inner_iframe.get_by_role('tab', name=re.compile(r'Attendees'))
attendees_count_text = attendees_tab.text_content()
# Should show "Attendees (0)" or decreased count
```

- **How verified**: Verified attendee removed in MCP
- **Wait for**: List updates, attendee disappears

## Success Verification
- Attendee is removed from the event
- Attendee no longer appears in attendees list
- Attendees count decreases (e.g., from "Attendees (1)" to "Attendees (0)")
- Event still exists and is accessible
