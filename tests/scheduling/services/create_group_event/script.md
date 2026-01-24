# Create Group Event - Detailed Script

## Overview
Create a new group event service with name, duration, price, and max attendees. Group events differ from 1-on-1 services by allowing multiple participants per time slot.

## Prerequisites
- User is logged in (from category _setup)
- Browser is on Settings > Services page (from delete_service test)

## Initial State
- URL: https://app.vcita.com/app/settings/services
- Page shows services list with "My Services" category

---

## Step 1: Verify on Services Page

- **Action**: Verify
- **Target**: Page URL and iframe

**VERIFIED PLAYWRIGHT CODE**:
```python
# Verify we're on Services page (previous test should have left us here)
if "/app/settings/services" not in page.url:
    raise ValueError(f"Expected to be on Services page, but URL is {page.url}")

page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
iframe = page.frame_locator('iframe[title="angularjs"]')
```

- **How verified**: Checked URL pattern and iframe presence in MCP
- **Wait for**: iframe with title="angularjs" is visible

---

## Step 2: Click New Service Dropdown

- **Action**: Click
- **Target**: "New service" dropdown button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="New service icon-caret-down")` | Role-based, includes dropdown indicator | Long name |
| `iframe.get_by_text("New service")` | Simpler text match | May match other text elements |
| `iframe.locator('button:has-text("New service")')` | CSS-based | Less semantic |

**CHOSEN**: `iframe.get_by_role("button", name="New service icon-caret-down")` - Role-based with exact match verified in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
new_service_btn = iframe.get_by_role("button", name="New service icon-caret-down")
new_service_btn.click()
```

- **How verified**: Clicked in MCP, dropdown menu appeared with "1 on 1 appointment" and "Group event" options
- **Wait for**: Menu element becomes visible
- **Fallback locators**: `iframe.locator('button:has-text("New service")')`

---

## Step 3: Wait for Dropdown Menu

- **Action**: Wait
- **Target**: Dropdown menu

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("menu")` | Semantic role for dropdown | None |
| `iframe.locator('[role="menu"]')` | CSS equivalent | Less readable |

**CHOSEN**: `iframe.get_by_role("menu")` - Standard role for dropdown menus

**VERIFIED PLAYWRIGHT CODE**:
```python
menu = iframe.get_by_role("menu")
menu.wait_for(state="visible", timeout=5000)
```

- **How verified**: Menu appeared in MCP snapshot after clicking button
- **Wait for**: Menu is visible

---

## Step 4: Select "Group event"

- **Action**: Click
- **Target**: Menu item for Group event

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("menuitem", name="Group event")` | Role-based, exact text | None |
| `iframe.get_by_text("Group event")` | Simpler | Less specific, may match other elements |
| `iframe.locator('md-menu-item:has-text("Group event")')` | Angular-specific | Framework dependent |

**CHOSEN**: `iframe.get_by_role("menuitem", name="Group event")` - Semantic role with exact name match

**VERIFIED PLAYWRIGHT CODE**:
```python
group_event_option = iframe.get_by_role("menuitem", name="Group event")
group_event_option.click()
```

- **How verified**: Clicked in MCP, group event creation dialog appeared with title "New service - Group event"
- **Wait for**: Dialog appears
- **Fallback locators**: `iframe.get_by_text("Group event")`

---

## Step 5: Wait for Dialog

- **Action**: Wait
- **Target**: Group event creation dialog

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("dialog")` | Semantic role | May match multiple dialogs |
| `iframe.locator('md-dialog')` | Angular component | Framework specific |

**CHOSEN**: `iframe.get_by_role("dialog")` - Standard dialog role

**VERIFIED PLAYWRIGHT CODE**:
```python
dialog = iframe.get_by_role("dialog")
dialog.wait_for(state="visible", timeout=10000)
```

- **How verified**: Dialog appeared in MCP with form fields
- **Wait for**: Dialog is visible

---

## Step 6: Fill Service Name

- **Action**: Type
- **Target**: Service name textbox
- **Value**: "Test Group Workshop {timestamp}"

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("textbox", name="Service name *")` | Role-based with label | Includes asterisk |
| `iframe.get_by_label("Service name")` | Label-based | May be partial match |
| `iframe.locator('input[ng-model*="name"]')` | Angular binding | Framework specific |

**CHOSEN**: `iframe.get_by_role("textbox", name="Service name *")` - Verified exact match in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
import time
timestamp = int(time.time())
group_event_name = f"Test Group Workshop {timestamp}"

name_field = iframe.get_by_role("textbox", name="Service name *")
name_field.click()
page.wait_for_timeout(100)  # Brief delay for field focus
name_field.press_sequentially(group_event_name, delay=30)
```

- **How verified**: Typed in MCP, name appeared in field, character counter updated to show "30 / 250"
- **Wait for**: Text appears in field (auto-wait on press_sequentially)
- **Fallback locators**: `iframe.get_by_label("Service name")`

---

## Step 7: Set Max Attendees

- **Action**: Fill
- **Target**: Max attendees spinbutton
- **Value**: 10

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")` | Role-based, unique | Long name with icon |
| `iframe.locator('input[type="number"]').first()` | Type-based | May match price field too |
| `iframe.get_by_label("Max attendees")` | Label-based | Partial match |

**CHOSEN**: `iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")` - Verified unique match in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
max_attendees_field = iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")
max_attendees_field.click()
max_attendees_field.fill("10")
```

- **How verified**: Filled in MCP, value "10" appeared in field
- **Wait for**: Value visible in spinbutton
- **Fallback locators**: `iframe.locator('input[type="number"]').first()`

---

## Step 8: Select Location - Face to Face

- **Action**: Click
- **Target**: "Face to face" location button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="icon-Home Face to face")` | Role-based with icon name | Long name |
| `iframe.get_by_text("Face to face")` | Text-based | May be less specific |
| `iframe.locator('button:has-text("Face to face")')` | CSS with text | Less semantic |

**CHOSEN**: `iframe.get_by_role("button", name="icon-Home Face to face")` - Verified in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
face_to_face_btn = iframe.get_by_role("button", name="icon-Home Face to face")
face_to_face_btn.click()
```

- **How verified**: Clicked in MCP, button became active, address radiogroup appeared
- **Wait for**: Radiogroup with address options becomes visible
- **Fallback locators**: `iframe.get_by_text("Face to face")`

---

## Step 9: Wait for Address Options

- **Action**: Wait
- **Target**: Address radiogroup

**VERIFIED PLAYWRIGHT CODE**:
```python
address_options = iframe.get_by_role("radiogroup")
address_options.wait_for(state="visible", timeout=5000)
# Default "My business address" is already selected - no action needed
```

- **How verified**: Radiogroup appeared in MCP with "My business address" checked
- **Wait for**: Radiogroup is visible

---

## Step 10: Select "With fee" and Enter Price

- **Action**: Click and Fill
- **Target**: "With fee" button and price field

**LOCATOR DECISION for "With fee" button:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="icon-Credit-card With fee")` | Role-based with icon | Long name |
| `iframe.get_by_text("With fee")` | Text-based | May match multiple |

**CHOSEN**: `iframe.get_by_role("button", name="icon-Credit-card With fee")` - Verified unique match

**LOCATOR DECISION for price field:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("spinbutton", name="Service price *")` | Role-based with label | None |
| `iframe.locator('input[type="number"]').last()` | Position-based | Fragile |

**CHOSEN**: `iframe.get_by_role("spinbutton", name="Service price *")` - Semantic with label

**VERIFIED PLAYWRIGHT CODE**:
```python
# Click "With fee" to enable pricing
with_fee_btn = iframe.get_by_role("button", name="icon-Credit-card With fee")
with_fee_btn.click()

# Wait for price field to appear
price_field = iframe.get_by_role("spinbutton", name="Service price *")
price_field.wait_for(state="visible", timeout=5000)
price_field.click()
price_field.fill("25")
```

- **How verified**: Clicked and filled in MCP, price "25" appeared in field
- **Wait for**: Price spinbutton field becomes visible, then value appears
- **Fallback locators**: `iframe.get_by_text("With fee")`, `iframe.locator('input[type="number"]').last()`

---

## Step 11: Click Create

- **Action**: Click
- **Target**: Create button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="Create")` | Role-based, unique | None |
| `iframe.locator('button:has-text("Create")')` | CSS with text | Less semantic |

**CHOSEN**: `iframe.get_by_role("button", name="Create")` - Standard button role

**VERIFIED PLAYWRIGHT CODE**:
```python
create_btn = iframe.get_by_role("button", name="Create")
create_btn.click()

# Wait for creation dialog to close
dialog.wait_for(state="hidden", timeout=15000)
```

- **How verified**: Clicked in MCP, dialog closed, new dialog appeared for event times
- **Wait for**: Dialog closes (state="hidden")
- **Fallback locators**: `iframe.locator('button:has-text("Create")')`

---

## Step 12: Handle "Enter Event Times" Dialog (CONDITIONAL)

- **Action**: Click (if dialog appears)
- **Target**: "I'll do it later" button
- **Note**: This dialog appears ONLY on first group event creation for an account. On subsequent creations, it does NOT appear. The test must handle both cases.

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="I'll do it later")` | Role-based, exact text | Apostrophe in text |
| `iframe.get_by_text("I'll do it later")` | Text match | Less specific |

**CHOSEN**: `iframe.get_by_role("button", name="I'll do it later")` - Verified in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
# This dialog appears only on first group event creation, not always
# We need to handle both cases: dialog appears OR dialog doesn't appear
later_btn = iframe.get_by_role("button", name="I'll do it later")

# Wait a short time to see if the dialog appears
try:
    later_btn.wait_for(state="visible", timeout=3000)
    print("  Event times dialog appeared - dismissing...")
    later_btn.click()
    page.wait_for_timeout(500)  # Brief settle time
except:
    # Dialog didn't appear - this is OK, continue
    print("  Event times dialog did not appear - continuing...")

# Wait for any remaining dialogs to close
page.wait_for_timeout(500)  # Brief settle time for dialogs to close
```

- **How verified**: Tested in MCP - dialog appeared on first creation, did not appear on subsequent creations
- **Wait for**: Short timeout (3s) to check if button appears, then continue regardless
- **Fallback locators**: `iframe.get_by_text("I'll do it later")`

---

## Step 13: Refresh Services List (Workaround for UI Bug)

- **Action**: Navigate
- **Target**: Settings main page then back to Services

**LOCATOR DECISION for Settings menu:**

| Option | Pros | Cons |
|--------|------|------|
| `page.get_by_text("Settings", exact=True)` | Exact text match | Multiple "Settings" may exist |
| `page.locator('[data-nav="settings"]')` | Data attribute | May not exist |

**CHOSEN**: `page.get_by_text("Settings", exact=True)` - Verified in MCP

**LOCATOR DECISION for Services button:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="Define the services your")` | Role-based, partial text | Truncated name |
| `iframe.get_by_text("Services")` | Simple text | May match multiple |

**CHOSEN**: `iframe.get_by_role("button", name="Define the services your")` - Verified unique match in settings page

**VERIFIED PLAYWRIGHT CODE**:
```python
# BUG WORKAROUND: After service creation, the list doesn't refresh automatically
# Navigate away and back to force a refresh
settings_menu = page.get_by_text("Settings", exact=True)
settings_menu.click()

# Wait for Settings main page
page.wait_for_url("**/app/settings", timeout=10000)

# Navigate back to Services
angular_iframe = page.locator('iframe[title="angularjs"]')
angular_iframe.wait_for(state="visible", timeout=10000)
iframe = page.frame_locator('iframe[title="angularjs"]')
services_btn = iframe.get_by_role("button", name="Define the services your")
services_btn.click()

# Wait for Services page to load
page.wait_for_url("**/app/settings/services", timeout=10000)
services_heading = iframe.get_by_role("heading", name="Settings / Services")
services_heading.wait_for(state="visible", timeout=10000)
```

- **How verified**: Navigated to Settings and back in MCP, services list showed new group event
- **Wait for**: Services heading becomes visible

---

## Step 14: Verify Group Event Created and Get ID

- **Action**: Verify and Extract
- **Target**: Group event in list

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button").filter(has_text=group_event_name)` | Filter by dynamic name | Requires variable |
| `iframe.locator(f'button:has-text("{group_event_name}")')` | CSS with variable | String interpolation |

**CHOSEN**: `iframe.get_by_role("button").filter(has_text=group_event_name)` - Role-based with filter

**VERIFIED PLAYWRIGHT CODE** (Validated with MCP):
```python
from playwright.sync_api import expect
import re

# HEALED: Services list uses endless scroll - must scroll to find group event
# Wait for "My Services" text to confirm the list section has loaded
iframe.get_by_text("My Services").wait_for(state="visible", timeout=10000)

# Scroll multiple times until group event is found or end of list reached
max_scrolls = 10
previous_last_text = ""
no_change_count = 0
group_event_in_list = None

for scroll_attempt in range(max_scrolls):
    # First, try to find the group event - if found, we're done
    try:
        group_event_in_list = iframe.get_by_role("button").filter(has_text=group_event_name)
        if group_event_in_list.count() > 0:
            break
    except:
        pass
    
    # Get all service buttons to find the last one
    all_services = iframe.get_by_role("button").filter(has_text=re.compile("Test Consultation|Appointment Test|Free estimate|Another Test|Test Debug|Test Group Workshop|Lawn mowing|On-site|MCP Test|UNIQUE TEST|SCROLL TEST"))
    
    try:
        service_count = all_services.count()
        
        if service_count > 0:
            last_service = all_services.nth(service_count - 1)
            current_last_text = last_service.text_content()
            
            if current_last_text == previous_last_text and previous_last_text != "":
                no_change_count += 1
                if no_change_count >= 2:
                    break
            else:
                no_change_count = 0
                previous_last_text = current_last_text
            
            last_service.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
        else:
            add_button = iframe.get_by_role('button', name='Add 1 on 1 Appointment')
            add_button.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
    except:
        add_button = iframe.get_by_role('button', name='Add 1 on 1 Appointment')
        add_button.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)

# Wait for the group event to appear in the list
# Group events show "X attendees" instead of "1 on 1"
group_event_in_list = iframe.get_by_role("button").filter(has_text=group_event_name)
group_event_in_list.wait_for(state="visible", timeout=10000)

# Verify it shows "10 attendees" (group event indicator)
expect(group_event_in_list).to_contain_text("10 attendees")

# Click on group event to open advanced edit
group_event_in_list.click()
page.wait_for_url("**/app/settings/services/**")

# Wait for advanced edit page to load
advanced_name_field = iframe.get_by_role("textbox", name="Service name *")
advanced_name_field.wait_for(state="visible", timeout=10000)

# Get group event ID from URL
url = page.url
group_event_id_match = re.search(r'/services/([a-z0-9]+)', url)
group_event_id = group_event_id_match.group(1) if group_event_id_match else None
```

- **How verified**: Group event visible in list showing "10 attendees" instead of "1 on 1"
- **Wait for**: Group event button visible, then URL changes to service edit page

---

## Step 15: Add Description (Advanced Edit)

- **Action**: Type
- **Target**: Service description textbox
- **Value**: "Group workshop for testing purposes."

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("textbox", name="Service description (optional)")` | Role-based with full label | Long name |
| `iframe.get_by_label("Service description")` | Label-based | Partial match |

**CHOSEN**: `iframe.get_by_role("textbox", name="Service description (optional)")` - Verified in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
group_event_description = "Group workshop for testing purposes."

# Find and fill description field
description_field = iframe.get_by_role("textbox", name="Service description (optional)")
description_field.click()
page.wait_for_timeout(100)  # Brief delay for field focus
description_field.press_sequentially(group_event_description, delay=20)
```

- **How verified**: Typed in MCP, description appeared in field
- **Wait for**: Text appears in field (auto-wait on press_sequentially)
- **Fallback locators**: `iframe.get_by_label("Service description")`

---

## Step 16: Save Advanced Edit

- **Action**: Click
- **Target**: Save button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="Save")` | Role-based, simple | May match multiple |
| `iframe.locator('button:has-text("Save")').first()` | First match | Less semantic |

**CHOSEN**: `iframe.get_by_role("button", name="Save")` - Standard save button

**VERIFIED PLAYWRIGHT CODE**:
```python
save_btn = iframe.get_by_role("button", name="Save")
save_btn.click()

# Wait for save to complete - the page refreshes, so wait for the name field to reappear
advanced_name_field = iframe.get_by_role("textbox", name="Service name *")
advanced_name_field.wait_for(state="visible", timeout=10000)
page.wait_for_timeout(500)  # Brief settle time after save
```

- **How verified**: Clicked Save in MCP, page refreshed with saved values
- **Wait for**: Service name field reappears after save (page refresh)

---

## Step 17: Navigate Back to Services List

- **Action**: Navigate
- **Target**: Back to Services list to leave in correct state for next tests

**VERIFIED PLAYWRIGHT CODE**:
```python
# Navigate back to services list via Settings
settings_menu = page.get_by_text("Settings", exact=True)
settings_menu.click()
page.wait_for_url("**/app/settings", timeout=10000)

# Re-acquire iframe reference after navigation
angular_iframe = page.locator('iframe[title="angularjs"]')
angular_iframe.wait_for(state="visible", timeout=10000)
iframe = page.frame_locator('iframe[title="angularjs"]')

# Click Services button to navigate back
services_btn = iframe.get_by_role("button", name="Define the services your")
services_btn.click()
page.wait_for_url("**/app/settings/services", timeout=10000)

# Wait for services page to load
services_heading = iframe.get_by_role("heading", name="Settings / Services")
services_heading.wait_for(state="visible", timeout=15000)
```

- **How verified**: Navigated in MCP, services list appeared
- **Wait for**: Services heading becomes visible

---

## Context Updates

```python
context["created_group_event_id"] = group_event_id
context["created_group_event_name"] = group_event_name
context["created_group_event_description"] = group_event_description
context["created_group_event_duration"] = 60  # 1 hour in minutes
context["created_group_event_price"] = 25
context["created_group_event_max_attendees"] = 10
```

---

## Key Differences from 1-on-1 Services

1. **Menu option**: Select "Group event" instead of "1 on 1 appointment"
2. **Max attendees field**: Group events have a "Max attendees" spinbutton (not present in 1-on-1)
3. **List display**: Shows "X attendees" instead of "1 on 1"
4. **Event times dialog**: After creation, a dialog prompts to enter event dates/times (can skip with "I'll do it later")
