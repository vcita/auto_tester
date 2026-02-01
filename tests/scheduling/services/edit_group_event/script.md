# Edit Group Event - Detailed Script

## Overview
Edit an existing group event to modify its duration, price, and max attendees, verifying that changes are saved correctly.

## Prerequisites
- User is logged in (from category _setup)
- Group event exists with `created_group_event_id` in context (from create_group_event test)
- Browser is on Settings > Services page (from create_group_event test)

## Initial State
- URL: https://app.vcita.com/app/settings/services
- Group event "{context.created_group_event_name}" visible in services list

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

## Step 2: Find and Click on Group Event

- **Action**: Click
- **Target**: Group event in services list

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button").filter(has_text=group_event_name)` | Filter by dynamic name, role-based | Requires variable |
| `iframe.locator(f'button:has-text("{group_event_name}")')` | CSS with variable | String interpolation needed |
| `iframe.get_by_text(group_event_name)` | Simple text match | May not be clickable |

**CHOSEN**: `iframe.get_by_role("button").filter(has_text=group_event_name)` - Role-based with filter, verified in MCP

**VERIFIED PLAYWRIGHT CODE** (Validated with MCP):
```python
# Get group event name from context
group_event_name = context["created_group_event_name"]

# HEALED: Services list uses endless scroll - must scroll to find group event
# Wait for "My Services" text to confirm the list section has loaded
iframe.get_by_text("My Services").wait_for(state="visible", timeout=10000)

# Scroll multiple times until group event is found or end of list reached
import re
max_scrolls = 10
previous_last_text = ""
no_change_count = 0
group_event_in_list = None

for scroll_attempt in range(max_scrolls):
    # First, try to find the group event - if found, we're done
    # HEALED: Use get_by_text() instead of filter(has_text=...) - filter pattern doesn't work
    try:
        group_event_in_list = iframe.get_by_text(group_event_name)
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
            page.wait_for_timeout(300)  # Brief settle (allowed) - then check group event in next iteration
        else:
            add_button = iframe.get_by_role('button', name='Add 1 on 1 Appointment')
            add_button.scroll_into_view_if_needed()
            page.wait_for_timeout(300)  # Brief settle (allowed)
    except:
        add_button = iframe.get_by_role('button', name='Add 1 on 1 Appointment')
        add_button.scroll_into_view_if_needed()
        page.wait_for_timeout(300)  # Brief settle (allowed)

# Find and click on the group event
group_event_in_list = iframe.get_by_role("button").filter(has_text=group_event_name)
group_event_in_list.wait_for(state="visible", timeout=10000)
group_event_in_list.click()
```

- **How verified**: Clicked in MCP, edit page opened
- **Wait for**: Group event button visible, then page navigates
- **Fallback locators**: `iframe.get_by_text(group_event_name)`

---

## Step 3: Wait for Edit Page to Load

- **Action**: Wait
- **Target**: Edit page with service name field

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("textbox", name="Service name *")` | Role-based field indicator | None |
| `page.wait_for_url("**/app/settings/services/**")` | URL-based | Doesn't verify content loaded |

**CHOSEN**: Both URL wait AND field visibility check for reliability

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for edit page to load
page.wait_for_url("**/app/settings/services/**")
name_field = iframe.get_by_role("textbox", name="Service name *")
name_field.wait_for(state="visible", timeout=10000)
```

- **How verified**: Edit page loaded in MCP with all fields visible
- **Wait for**: URL changes AND service name field is visible

---

## Step 4: Change Max Attendees from 10 to 15

- **Action**: Fill
- **Target**: Max attendees spinbutton
- **Value**: 15

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")` | Role-based, unique | Long name with icon |
| `iframe.locator('input[type="number"]').first()` | Type-based | Position dependent |
| `iframe.get_by_label("Max attendees")` | Label-based | Partial match |

**CHOSEN**: `iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")` - Verified unique match in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
max_attendees_field = iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")
max_attendees_field.click()
max_attendees_field.fill("15")  # fill is OK for number spinbutton
```

- **How verified**: Filled in MCP, value changed from "10" to "15"
- **Wait for**: Value visible in spinbutton
- **Fallback locators**: `iframe.locator('input[type="number"]').first()`

---

## Step 5: Change Duration Minutes from 0 to 30

- **Action**: Select
- **Target**: Minutes dropdown
- **Value**: 30 Minutes

**LOCATOR DECISION for Minutes dropdown:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("listbox", name="Minutes :")` | Role-based with partial name | Colon in name |
| `iframe.locator('md-select[ng-model*="minutes"]')` | Angular binding | Framework specific |

**CHOSEN**: `iframe.get_by_role("listbox", name="Minutes :")` - Role-based, verified in MCP

**LOCATOR DECISION for 30 Minutes option:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("option", name="30 Minutes")` | Role-based, exact text | None |
| `iframe.get_by_text("30 Minutes")` | Text match | Less specific |

**CHOSEN**: `iframe.get_by_role("option", name="30 Minutes")` - Semantic option role

**VERIFIED PLAYWRIGHT CODE**:
```python
# Click Minutes dropdown
minutes_dropdown = iframe.get_by_role("listbox", name="Minutes :")
minutes_dropdown.click()

# Wait for options to appear
minutes_option = iframe.get_by_role("option", name="30 Minutes")
minutes_option.wait_for(state="visible", timeout=5000)
minutes_option.click()
```

- **How verified**: Selected in MCP, dropdown closed with "30 Minutes" displayed
- **Wait for**: Option element becomes visible before clicking
- **Fallback locators**: `iframe.get_by_text("30 Minutes")`

---

## Step 6: Change Price from 25 to 35

- **Action**: Fill
- **Target**: Service price spinbutton
- **Value**: 35

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("spinbutton", name="Service price (ILS) *")` | Role-based with currency | None |
| `iframe.locator('input[type="number"]').last()` | Position-based | Fragile |
| `iframe.get_by_label("Service price")` | Label-based | Partial match |

**CHOSEN**: `iframe.get_by_role("spinbutton", name="Service price (ILS) *")` - Verified unique match in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
price_field = iframe.get_by_role("spinbutton", name="Service price (ILS) *")
price_field.click()
price_field.fill("35")  # fill is OK for number spinbutton
```

- **How verified**: Filled in MCP, value changed from "25" to "35"
- **Wait for**: Value visible in spinbutton
- **Fallback locators**: `iframe.get_by_label("Service price")`

---

## Step 7: Save Changes

- **Action**: Click
- **Target**: Save button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="Save")` | Role-based, simple | None |
| `iframe.locator('button:has-text("Save")')` | CSS with text | Less semantic |

**CHOSEN**: `iframe.get_by_role("button", name="Save")` - Standard button role

**VERIFIED PLAYWRIGHT CODE**:
```python
save_btn = iframe.get_by_role("button", name="Save")
save_btn.click()

# Wait for save to complete - the page refreshes
name_field = iframe.get_by_role("textbox", name="Service name *")
name_field.wait_for(state="visible", timeout=10000)
page.wait_for_timeout(500)  # Brief settle time after save
```

- **How verified**: Clicked Save in MCP, page refreshed with saved values
- **Wait for**: Service name field reappears after save (page refresh)
- **Fallback locators**: `iframe.locator('button:has-text("Save")')`

---

## Step 8: Verify Changes by Re-checking Field Values

- **Action**: Verify
- **Target**: Max attendees, duration, and price fields

**VERIFIED PLAYWRIGHT CODE**:
```python
from playwright.sync_api import expect

# Verify max attendees
expect(iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")).to_have_value("15")

# Verify duration shows 30 minutes
expect(iframe.get_by_role("listbox", name="Minutes :")).to_contain_text("30 Minutes")

# Verify price
expect(iframe.get_by_role("spinbutton", name="Service price (ILS) *")).to_have_value("35")
```

- **How verified**: Re-checked fields after save in MCP, all values persisted
- **Wait for**: Assertions pass

---

## Step 9: Navigate Back to Services List

- **Action**: Navigate
- **Target**: Back to Services list

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `page.get_by_text("Settings", exact=True)` | Exact text match | None |
| `page.locator('.nav-item:has-text("Settings")')` | CSS class | Less semantic |

**CHOSEN**: `page.get_by_text("Settings", exact=True)` - Verified in MCP

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

# Click Services button
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

## Step 10: Verify Changes in Services List

- **Action**: Verify
- **Target**: Group event in list shows updated values

**VERIFIED PLAYWRIGHT CODE**:
```python
# HEALED: After navigating back, the list may need scrolling to find the group event
# Wait for "My Services" text to confirm the list section has loaded
iframe.get_by_text("My Services").wait_for(state="visible", timeout=10000)

# Scroll multiple times until group event is found or end of list reached
max_scrolls = 10
previous_last_text = ""
no_change_count = 0

for scroll_attempt in range(max_scrolls):
    # First, try to find the group event - if found, we're done
    # HEALED: Use get_by_text() instead of filter(has_text=...) - filter pattern doesn't work
    try:
        group_event_in_list = iframe.get_by_text(group_event_name)
        if group_event_in_list.count() > 0:
            print(f"  Found group event after {scroll_attempt} scrolls")
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
                    print(f"  Reached end of list after {scroll_attempt + 1} scrolls (no new items)")
                    break
            else:
                no_change_count = 0
                previous_last_text = current_last_text
            
            last_service.scroll_into_view_if_needed()
            page.wait_for_timeout(300)  # Brief settle (allowed) - then check in next iteration
        else:
            add_button = iframe.get_by_role('button', name='Add 1 on 1 Appointment')
            add_button.scroll_into_view_if_needed()
            page.wait_for_timeout(300)  # Brief settle (allowed)
    except Exception as e:
        add_button = iframe.get_by_role('button', name='Add 1 on 1 Appointment')
        add_button.scroll_into_view_if_needed()
        page.wait_for_timeout(300)  # Brief settle (allowed)

# Find the group event in the list (all items should be loaded)
# HEALED: Use get_by_text() instead of filter(has_text=...) - filter pattern doesn't work
group_event_in_list = iframe.get_by_text(group_event_name)
group_event_in_list.wait_for(state="visible", timeout=10000)

# Verify group event exists in list (changes were already verified in Step 8 on edit page)
# HEALED: The services list view does NOT display max attendees in the button text
# The list only shows the service name, not detailed information like attendee count
# Changes are verified in Step 8 by re-checking field values on the edit page
```

- **How verified**: Observed in test run - list view only shows service name, not attendee count. Changes verified in Step 8.
- **Wait for**: Group event is visible in list

---

## Context Updates

```python
context["edited_group_event_duration"] = 90  # 1 hour 30 min = 90 minutes
context["edited_group_event_price"] = 35
context["edited_group_event_max_attendees"] = 15
```
