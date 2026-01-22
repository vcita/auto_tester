# Create Service - Detailed Script

## Overview
Create a new 1-on-1 service with name, duration, and price. After creation, navigate to advanced edit to add a description.

## Prerequisites
- User is logged in (from category _setup)
- Browser is on Settings > Services page (from category _setup)

---

## Step 1: Verify on Services Page

- **Action**: Verify
- **Target**: Already on Services page from setup

**VERIFIED PLAYWRIGHT CODE**:
```python
# Verify we're on Services page (setup should have left us here)
if "/app/settings/services" not in page.url:
    raise ValueError(f"Expected to be on Services page, but URL is {page.url}")

page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
iframe = page.frame_locator('iframe[title="angularjs"]')
```

- **Wait for**: iframe with angularjs title is visible

---

## Step 2: Click New Service Dropdown

- **Action**: Click
- **Target**: "New service" dropdown button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.getByRole('button', { name: 'New service icon-caret-down' })` | Exact match | Long name |
| `iframe.getByText('New service')` | Simpler | May match other elements |

**CHOSEN**: `iframe.getByRole('button', { name: 'New service icon-caret-down' })` - Verified exact match in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
new_service_btn = iframe.get_by_role("button", name="New service icon-caret-down")
new_service_btn.click()
# Wait for dropdown menu to appear
menu = iframe.get_by_role("menu")
menu.wait_for(state="visible", timeout=5000)
```

- **How verified**: Clicked in MCP, dropdown menu appeared
- **Wait for**: Menu element becomes visible

---

## Step 3: Select "1 on 1 appointment"

- **Action**: Click
- **Target**: Menu item for 1 on 1 appointment

**VERIFIED PLAYWRIGHT CODE**:
```python
one_on_one_option = iframe.get_by_role("menuitem", name="on 1 appointment")
one_on_one_option.click()
# Wait for dialog to appear
dialog = iframe.get_by_role("dialog")
dialog.wait_for(state="visible", timeout=10000)
```

- **How verified**: Clicked in MCP, service creation dialog appeared
- **Wait for**: Dialog with role="dialog" becomes visible

---

## Step 4: Fill Service Name

- **Action**: Type
- **Target**: Service name textbox
- **Value**: "Test Consultation {timestamp}"

**VERIFIED PLAYWRIGHT CODE**:
```python
import time
timestamp = int(time.time())
service_name = f"Test Consultation {timestamp}"

name_field = iframe.get_by_role("textbox", name="Service name *")
name_field.click()
page.wait_for_timeout(100)  # Brief delay for field focus
name_field.press_sequentially(service_name, delay=30)
```

- **How verified**: Typed in MCP, name appeared in field
- **Wait for**: Service name visible in textbox (auto-wait on press_sequentially)

---

## Step 5: Select Location - Face to Face

- **Action**: Click
- **Target**: "Face to face" location button

**VERIFIED PLAYWRIGHT CODE**:
```python
face_to_face_btn = iframe.get_by_role("button", name="icon-Home Face to face")
face_to_face_btn.click()
# Wait for address options to appear (radiogroup)
address_options = iframe.get_by_role("radiogroup")
address_options.wait_for(state="visible", timeout=5000)
```

- **How verified**: Clicked in MCP, button became active, address options appeared
- **Wait for**: Radiogroup with address options becomes visible

---

## Step 6: Set Duration - Hours to 0

- **Action**: Select
- **Target**: Hours dropdown

**VERIFIED PLAYWRIGHT CODE**:
```python
# Click Hours dropdown
hours_dropdown = iframe.get_by_role("listbox", name="Hours:")
hours_dropdown.click()
# Wait for options to appear
hours_option = iframe.get_by_role("option", name="0 Hours", exact=True)
hours_option.wait_for(state="visible", timeout=5000)
hours_option.click()
```

- **How verified**: Selected in MCP, dropdown closed with "0 Hours" selected
- **Wait for**: Option element becomes visible before clicking

---

## Step 7: Set Duration - Minutes to 30

- **Action**: Select
- **Target**: Minutes dropdown

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

- **How verified**: Selected in MCP, dropdown closed with "30 Minutes" selected
- **Wait for**: Option element becomes visible before clicking

---

## Step 8: Select "With fee" and Enter Price

- **Action**: Click and Type
- **Target**: "With fee" button and price field

**VERIFIED PLAYWRIGHT CODE**:
```python
# Click "With fee" to enable pricing
with_fee_btn = iframe.get_by_role("button", name="icon-Credit-card With fee")
with_fee_btn.click()
# Wait for price field to appear
price_field = iframe.get_by_role("spinbutton", name="Service price *")
price_field.wait_for(state="visible", timeout=5000)
price_field.click()
price_field.fill("50")
```

- **How verified**: Clicked and filled in MCP, price "50" appeared in field
- **Wait for**: Price spinbutton field becomes visible

---

## Step 9: Click Create

- **Action**: Click
- **Target**: Create button

**VERIFIED PLAYWRIGHT CODE**:
```python
# Get reference to dialog before clicking create
dialog = iframe.get_by_role("dialog")

create_btn = iframe.get_by_role("button", name="Create")
create_btn.click()

# Wait for dialog to close (indicates creation completed)
dialog.wait_for(state="hidden", timeout=15000)
```

- **How verified**: Clicked in MCP, dialog closed, service appeared in list
- **Wait for**: Dialog closes (state="hidden")

---

## Step 10: Refresh Services List (Workaround for UI Bug)

- **Action**: Navigate
- **Target**: Navigate to Settings main page and back to Services to refresh the list
- **Note**: BUG - After creating a service, the list shows an empty row instead of the new service. Refreshing via navigation fixes this.

**VERIFIED PLAYWRIGHT CODE**:
```python
# BUG WORKAROUND: After service creation, the list doesn't refresh automatically
# Navigate away and back to force a refresh
settings_menu = page.locator("[data-testid='settings']").or_(page.get_by_text("Settings", exact=True))
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

- **How verified**: Navigated to Settings and back in MCP, services list showed new service
- **Wait for**: Services heading becomes visible

---

## Step 11: Verify Service Created and Open Advanced Edit

- **Action**: Verify and Click
- **Target**: New service appears in the list, then click to open advanced edit

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for the service to appear in the list (should be visible after refresh)
# Use the full service name to avoid matching other "Test Consultation" services
service_in_list = iframe.get_by_role("button").filter(has_text=service_name)
service_in_list.wait_for(state="visible", timeout=10000)

# Click on service to open advanced edit
service_in_list.click()
page.wait_for_url("**/app/settings/services/**")

# Wait for advanced edit page to load (Service name field visible)
advanced_name_field = iframe.get_by_role("textbox", name="Service name *")
advanced_name_field.wait_for(state="visible", timeout=10000)

# Get service ID from URL
import re
url = page.url
service_id_match = re.search(r'/services/([a-z0-9]+)', url)
service_id = service_id_match.group(1) if service_id_match else None
```

- **How verified**: Service visible in list after refresh, clicking opens edit page
- **Wait for**: Service button visible, then URL changes to service edit page

---

## Step 12: Add Service Description (Advanced Edit)

- **Action**: Type
- **Target**: Service description textbox
- **Value**: "Professional consultation service for testing purposes."

**VERIFIED PLAYWRIGHT CODE**:
```python
service_description = "Professional consultation service for testing purposes."

# Find and fill description field
description_field = iframe.get_by_role("textbox", name="Service description (optional)")
description_field.click()
page.wait_for_timeout(100)  # Brief delay for field focus
description_field.press_sequentially(service_description, delay=20)
```

- **How verified**: Typed in MCP, description appeared in field
- **Wait for**: Text appears in field (auto-wait on press_sequentially)

---

## Step 13: Save Advanced Edit

- **Action**: Click
- **Target**: Save button

**VERIFIED PLAYWRIGHT CODE**:
```python
save_btn = iframe.get_by_role("button", name="Save")
save_btn.click()

# Wait for save to complete - the page refreshes, so wait for the name field to reappear
# This indicates the save completed and the page reloaded
advanced_name_field = iframe.get_by_role("textbox", name="Service name *")
advanced_name_field.wait_for(state="visible", timeout=10000)
page.wait_for_timeout(500)  # Brief settle time after save
```

- **How verified**: Clicked Save in MCP, page refreshed with saved values
- **Wait for**: Service name field reappears after save (page refresh)

---

## Step 14: Navigate Back to Services List

- **Action**: Navigate
- **Target**: Back to Services list to leave in correct state for next tests

**VERIFIED PLAYWRIGHT CODE**:
```python
# Navigate back to services list
page.goto("https://app.vcita.com/app/settings/services")

# Wait for services page to load
services_heading = iframe.get_by_role("heading", name="Settings / Services")
services_heading.wait_for(state="visible", timeout=15000)
```

- **How verified**: Navigated in MCP, services list appeared
- **Wait for**: Services heading becomes visible

---

## Context Updates

```python
context["created_service_id"] = service_id
context["created_service_name"] = service_name
context["created_service_description"] = service_description
context["created_service_duration"] = 30
context["created_service_price"] = 50
```
