# Edit Service - Detailed Script

## Overview
Edit an existing service to modify its duration (30 min -> 45 min) and price ($50 -> $75), then verify changes are saved correctly.

## Prerequisites
- User is logged in (from category _setup)
- Service exists with `created_service_id` and `created_service_name` in context (from create_service test)
- Browser is on Settings > Services page (from create_service test)

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

## Step 2: Find and Click on Test Service

- **Action**: Hover and Click
- **Target**: Service created in previous test (using `created_service_name` from context)

**VERIFIED PLAYWRIGHT CODE**:
```python
# Find the service by name from context
service_name = context.get("created_service_name")
if not service_name:
    raise ValueError("created_service_name not found in context - run create_service first")

# HEALED: Services list uses endless scroll - must scroll to find service
# Wait for "My Services" text to confirm the list section has loaded
iframe.get_by_text("My Services").wait_for(state="visible", timeout=10000)

# Scroll multiple times until service is found or end of list reached
max_scrolls = 10
previous_last_text = ""
no_change_count = 0
service_row = None

for scroll_attempt in range(max_scrolls):
    # First, try to find the service - if found, we're done
    try:
        service_row = iframe.get_by_role("button").filter(has_text=service_name)
        if service_row.count() > 0:
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

# Now locate service in list and hover to reveal edit button
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

## Step 3: Wait for Edit Form to Load

- **Action**: Wait
- **Target**: Service edit form loads with current values

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for edit page heading
heading = iframe.get_by_role("heading", name="Settings / My services / Edit Service")
heading.wait_for(state="visible", timeout=10000)

# Verify service name field is visible
name_field = iframe.get_by_role("textbox", name="Service name *")
name_field.wait_for(state="visible", timeout=10000)
```

- **How verified**: Edit page loads with service details
- **Wait for**: Heading and name field visible

---

## Step 4: Change Duration from 30 to 45 Minutes

- **Action**: Select
- **Target**: Minutes dropdown - change from 30 to 45

**VERIFIED PLAYWRIGHT CODE**:
```python
# Click Minutes dropdown
minutes_dropdown = iframe.get_by_role("listbox", name="Minutes :")
minutes_dropdown.click()

# Wait for options and select 45 Minutes
minutes_option = iframe.get_by_role("option", name="45 Minutes")
minutes_option.wait_for(state="visible", timeout=5000)
minutes_option.click()
```

- **How verified**: Clicked dropdown in MCP, selected 45 Minutes
- **Wait for**: Option element becomes visible before clicking

---

## Step 5: Change Price from 50 to 75

- **Action**: Clear and Type
- **Target**: Service price field

**VERIFIED PLAYWRIGHT CODE**:
```python
# Find and clear price field, then enter new value
price_field = iframe.get_by_role("spinbutton", name="Service price")
price_field.click()
price_field.fill("")  # Clear existing value
price_field.fill("75")
```

- **How verified**: Cleared and typed new value in MCP
- **Wait for**: Value appears in field (auto-wait on fill)

---

## Step 6: Save Changes

- **Action**: Click
- **Target**: Save button

**VERIFIED PLAYWRIGHT CODE**:
```python
save_btn = iframe.get_by_role("button", name="Save")
save_btn.click()

# Wait for save to complete - page refreshes with updated values
# Wait for heading to reappear after save
heading = iframe.get_by_role("heading", name="Settings / My services / Edit Service")
heading.wait_for(state="visible", timeout=15000)
```

- **How verified**: Clicked Save in MCP, page refreshed with saved values
- **Wait for**: Heading reappears after save completes

---

## Step 7: Verify Changes Were Saved

- **Action**: Verify
- **Target**: Confirm duration shows 45 minutes and price shows 75

**VERIFIED PLAYWRIGHT CODE**:
```python
# Verify duration is now 45 minutes
minutes_dropdown = iframe.get_by_role("listbox", name="Minutes :")
expect(minutes_dropdown).to_contain_text("45 Minutes")

# Verify price is now 75
price_field = iframe.get_by_role("spinbutton", name="Service price")
expect(price_field).to_have_value("75")

print("  [OK] Changes verified: 45 minutes, price 75")
```

- **How verified**: Read values from form after save
- **Wait for**: Expect assertions auto-wait

---

## Step 8: Navigate Back to Services List

- **Action**: Navigate
- **Target**: Back to Services list to leave in correct state for next test

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
context["edited_service_duration"] = 45
context["edited_service_price"] = 75
```
