# Delete Group Event - Detailed Script

## Overview
Delete the test group event to clean up test data and verify deletion functionality.

## Prerequisites
- User is logged in (from category _setup)
- Group event exists with `created_group_event_id` in context (from create_group_event test)
- Browser is on Services page (from edit_group_event test)

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

**VERIFIED PLAYWRIGHT CODE**:
```python
# Get group event name from context
group_event_name = context["created_group_event_name"]

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

## Step 4: Click Delete Button

- **Action**: Click
- **Target**: Delete button in header

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="Delete")` | Role-based, exact match | None |
| `iframe.locator('button:has-text("Delete")')` | CSS with text | Less semantic |
| `iframe.get_by_text("Delete")` | Text match | May match multiple elements |

**CHOSEN**: `iframe.get_by_role("button", name="Delete")` - Role-based, verified in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
delete_btn = iframe.get_by_role("button", name="Delete")
delete_btn.click()
```

- **How verified**: Clicked in MCP, confirmation dialog appeared with "Are you sure you want to delete this service?"
- **Wait for**: Dialog becomes visible
- **Fallback locators**: `iframe.locator('button:has-text("Delete")')`

---

## Step 5: Wait for Confirmation Dialog

- **Action**: Wait
- **Target**: Confirmation dialog

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("dialog")` | Semantic role | None |
| `iframe.locator('md-dialog')` | Angular component | Framework specific |

**CHOSEN**: `iframe.get_by_role("dialog")` - Standard dialog role

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for confirmation dialog
dialog = iframe.get_by_role("dialog")
dialog.wait_for(state="visible", timeout=5000)
```

- **How verified**: Dialog appeared in MCP with confirmation message
- **Wait for**: Dialog is visible

---

## Step 6: Confirm Deletion

- **Action**: Click
- **Target**: "Ok" button in confirmation dialog

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="Ok")` | Role-based, exact text | None |
| `iframe.get_by_text("Ok")` | Text match | Less specific |
| `iframe.locator('.md-confirm-button')` | Angular class | Framework specific |

**CHOSEN**: `iframe.get_by_role("button", name="Ok")` - Role-based, verified in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
# Click Ok to confirm deletion
ok_btn = iframe.get_by_role("button", name="Ok")
ok_btn.click()
```

- **How verified**: Clicked Ok in MCP, redirected to services list
- **Wait for**: Dialog closes, page redirects
- **Fallback locators**: `iframe.get_by_text("Ok")`, `iframe.locator('.md-confirm-button')`

---

## Step 7: Wait for Redirect to Services List

- **Action**: Wait
- **Target**: Services list page

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for redirect back to services list
page.wait_for_url("**/app/settings/services", timeout=10000)
```

- **How verified**: URL changed to services list in MCP
- **Wait for**: URL matches services page pattern (not individual service URL)

---

## Step 8: Verify Group Event Was Deleted

- **Action**: Verify
- **Target**: Group event no longer appears in list

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button").filter(has_text=group_event_name)` | Same locator used before | None |
| Using `expect().to_have_count(0)` | Playwright assertion | None |

**CHOSEN**: Same locator with count assertion to verify absence

**VERIFIED PLAYWRIGHT CODE**:
```python
from playwright.sync_api import expect

# Wait for services list to load
services_heading = iframe.get_by_role("heading", name="Settings / Services")
services_heading.wait_for(state="visible", timeout=10000)

# Verify group event is no longer in the list
# The element should not exist
group_event_in_list = iframe.get_by_role("button").filter(has_text=group_event_name)
expect(group_event_in_list).to_have_count(0)
```

- **How verified**: Services list no longer contains group event after deletion
- **Wait for**: Services heading visible, then verify count is 0

---

## Context Cleanup

```python
# Clear all group event context variables
context.pop("created_group_event_id", None)
context.pop("created_group_event_name", None)
context.pop("created_group_event_description", None)
context.pop("created_group_event_duration", None)
context.pop("created_group_event_price", None)
context.pop("created_group_event_max_attendees", None)
context.pop("edited_group_event_duration", None)
context.pop("edited_group_event_price", None)
context.pop("edited_group_event_max_attendees", None)
```
