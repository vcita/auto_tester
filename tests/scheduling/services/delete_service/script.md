# Delete Service - Detailed Script

## Overview
Delete the test service to clean up test data and verify service deletion functionality.

## Prerequisites
- User is logged in (from category _setup)
- Service exists with `created_service_id` and `created_service_name` in context (from create_service test)
- Browser is on Settings > Services page (from edit_service test)

---

## Step 1: Verify on Services Page

- **Action**: Verify
- **Target**: Already on Services page from previous test

**VERIFIED PLAYWRIGHT CODE**:
```python
# Verify we're on Services page
if "/app/settings/services" not in page.url:
    raise ValueError(f"Expected to be on Services page, but URL is {page.url}")

page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
iframe = page.frame_locator('iframe[title="angularjs"]')
```

- **Wait for**: iframe with angularjs title is visible

---

## Step 2: Find and Open Test Service Edit Page

- **Action**: Hover and Click
- **Target**: Service created in previous tests (using `created_service_name` from context)

**VERIFIED PLAYWRIGHT CODE**:
```python
# Find the service by name from context
service_name = context.get("created_service_name")
if not service_name:
    raise ValueError("created_service_name not found in context - run create_service first")

# Locate service in list and hover to reveal edit button
service_row = iframe.get_by_role("button").filter(has_text=service_name)
service_row.hover()

# Wait for edit button to appear and click it
edit_btn = iframe.get_by_role("button", name="icon-pencil-s")
edit_btn.wait_for(state="visible", timeout=5000)
edit_btn.click()

# Wait for edit page to load
page.wait_for_url("**/app/settings/services/**")
```

- **How verified**: Hovered on service in MCP, edit pencil button appeared
- **Wait for**: Edit button visible, then URL changes to service edit page

---

## Step 3: Wait for Edit Page to Load

- **Action**: Wait
- **Target**: Service edit page loads

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for edit page heading
heading = iframe.get_by_role("heading", name="Settings / My services / Edit Service")
heading.wait_for(state="visible", timeout=10000)
```

- **How verified**: Edit page loads with Delete button visible
- **Wait for**: Heading visible

---

## Step 4: Click Delete Button

- **Action**: Click
- **Target**: Delete button in the toolbar

**VERIFIED PLAYWRIGHT CODE**:
```python
# Click Delete button
delete_btn = iframe.get_by_role("button", name="Delete")
delete_btn.click()

# Wait for confirmation dialog to appear
dialog = iframe.get_by_role("dialog")
dialog.wait_for(state="visible", timeout=5000)
```

- **How verified**: Clicked Delete in MCP, confirmation dialog appeared
- **Wait for**: Dialog with confirmation message visible

---

## Step 5: Confirm Deletion

- **Action**: Click
- **Target**: Ok button in confirmation dialog

**VERIFIED PLAYWRIGHT CODE**:
```python
# Confirm deletion by clicking Ok
ok_btn = iframe.get_by_role("button", name="Ok")
ok_btn.click()

# Wait for dialog to close and redirect to services list
dialog = iframe.get_by_role("dialog")
dialog.wait_for(state="hidden", timeout=10000)

# Wait for redirect to services list
page.wait_for_url("**/app/settings/services", timeout=15000)
```

- **How verified**: Clicked Ok in MCP, dialog closed, redirected to services list
- **Wait for**: Dialog hidden, URL changes to services list

---

## Step 6: Verify Service Was Deleted

- **Action**: Verify
- **Target**: Service no longer appears in the services list

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for services list to load
services_heading = iframe.get_by_role("heading", name="Settings / Services")
services_heading.wait_for(state="visible", timeout=10000)

# BUG WORKAROUND: Refresh list by navigating away and back (same bug as create_service)
settings_menu = page.get_by_text("Settings", exact=True)
settings_menu.click()
page.wait_for_url("**/app/settings", timeout=10000)

angular_iframe = page.locator('iframe[title="angularjs"]')
angular_iframe.wait_for(state="visible", timeout=10000)
iframe = page.frame_locator('iframe[title="angularjs"]')
services_btn = iframe.get_by_role("button", name="Define the services your")
services_btn.click()
page.wait_for_url("**/app/settings/services", timeout=10000)

services_heading = iframe.get_by_role("heading", name="Settings / Services")
services_heading.wait_for(state="visible", timeout=10000)

# Verify service is no longer in the list
service_in_list = iframe.get_by_role("button").filter(has_text=service_name)
expect(service_in_list).to_have_count(0)

print(f"  [OK] Service '{service_name}' successfully deleted")
```

- **How verified**: Searched for service name in MCP, not found in list
- **Wait for**: Services heading visible, then verify service count is 0

---

## Context Updates

```python
# Clear service-related context variables
context.pop("created_service_id", None)
context.pop("created_service_name", None)
context.pop("created_service_description", None)
context.pop("created_service_duration", None)
context.pop("created_service_price", None)
context.pop("edited_service_duration", None)
context.pop("edited_service_price", None)
```
