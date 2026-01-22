# Edit Matter - Detailed Script

## Prerequisites
- Must run after `create_matter` test
- Requires context data:
  - `created_matter_id`: The ID of the matter to edit
  - `created_matter_name`: The name for verification

## Initial State
- URL: Matter detail page `/app/clients/{matter_id}` (from previous test)
- User is logged in (via category setup)

## Test Data
Generate new values with timestamp for uniqueness:
```python
edit_data = {
    "help_request": f"EDITED: Need updated property services - {timestamp}",
    "special_instructions": f"EDITED: New gate code is 9999. Updated on {timestamp}",
}
```

## Actions

### Step 1: Verify on Matter Detail Page

- **Action**: Verify URL
- **Target**: Current URL should contain the matter ID

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| Check `page.url` contains matter_id | Simple, reliable | None |
| Check page title | Also valid | Slower |

**CHOSEN**: URL check - Direct and immediate verification.

**VERIFIED PLAYWRIGHT CODE**:
```python
if matter_id not in page.url:
    raise ValueError(f"Expected to be on matter page {matter_id}, but URL is {page.url}")
expect(page).to_have_url(re.compile(rf"/app/clients/{re.escape(matter_id)}"))
```

- **How verified**: Confirmed URL pattern matches after create_matter test
- **Wait for**: URL matches pattern

### Step 2: Wait for Page to Load

- **Action**: Wait
- **Target**: Page title should contain matter name

**VERIFIED PLAYWRIGHT CODE**:
```python
expect(page).to_have_title(re.compile(re.escape(matter_name)), timeout=15000)
```

- **How verified**: Page title updates to include matter name after load
- **Wait for**: Title contains matter name

### Step 3: Open Edit Property Dialog

- **Action**: Click
- **Target**: Edit button (pencil icon) next to property name in the matter card header

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `get_by_role("button", name="Edit")` | Semantic | Button has no accessible name |
| `locator(".edit-button")` | Clear intent | Class might not exist |
| `get_by_role("button").nth(2)` | Works reliably | Fragile if button order changes |

**CHOSEN**: `get_by_role("button").nth(2)` - The edit button is the third button in the header container. No unique identifier available.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for the outer iframe
angular_iframe = page.locator('iframe[title="angularjs"]')
angular_iframe.wait_for(state="visible", timeout=15000)

# Get the nested iframe structure
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')

# Wait for content to load - look for the property name button in the header
inner_iframe.get_by_role("button", name=matter_name).first.wait_for(timeout=15000)

# Find and click the edit button next to the property name
edit_button = inner_iframe.get_by_role("button").nth(2)
edit_button.wait_for(state="visible", timeout=10000)
edit_button.click()
```

- **How verified**: Clicked in MCP, "Edit property info" dialog opened successfully
- **Wait for**: Dialog with "Edit property info" title appears
- **Fallback locators**:
  - `locator(".matter-card-title").locator("button").nth(1)`
  - `locator("button").filter(has=locator("svg"))`

### Step 4: Wait for Edit Dialog

- **Action**: Wait
- **Target**: Edit dialog title "Edit property info"

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `locator("text=Edit property info")` | Matches visible text | None |
| `get_by_role("dialog")` | Semantic | Dialog may not have role |

**CHOSEN**: `locator("text=Edit property info")` - Direct text match is reliable.

**VERIFIED PLAYWRIGHT CODE**:
```python
dialog_title = outer_iframe.locator("text=Edit property info")
dialog_title.wait_for(state="visible", timeout=10000)
page.wait_for_timeout(200)  # Brief settle for dialog animation
```

- **How verified**: Dialog title appears after clicking edit button
- **Wait for**: Dialog title visible

### Step 5: Fill "How can we help you?" Field

- **Action**: Clear and type
- **Target**: "How can we help you?" textbox
- **Value**: `{edit_data["help_request"]}`

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `get_by_role("textbox", name="How can we help you?")` | Semantic, unique | None |
| `get_by_label("How can we help you?")` | Also works | Less specific |

**CHOSEN**: `get_by_role("textbox", name="How can we help you?")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
help_field = outer_iframe.get_by_role("textbox", name="How can we help you?")
help_field.click()
help_field.fill("")  # Clear existing content
help_field.press_sequentially(edit_data["help_request"], delay=20)
```

- **How verified**: Typed in MCP, value appeared in field
- **Wait for**: Field contains new value
- **Fallback locators**: `get_by_label("How can we help you?")`

### Step 6: Fill "Special instructions/requests" Field

- **Action**: Clear and type
- **Target**: "Special instructions/requests" textbox
- **Value**: `{edit_data["special_instructions"]}`

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `get_by_role("textbox", name="Special instructions/requests")` | Semantic, unique | None |
| `get_by_label("Special instructions/requests")` | Also works | Less specific |

**CHOSEN**: `get_by_role("textbox", name="Special instructions/requests")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
instructions_field = outer_iframe.get_by_role("textbox", name="Special instructions/requests")
instructions_field.click()
instructions_field.fill("")  # Clear existing content
instructions_field.press_sequentially(edit_data["special_instructions"], delay=20)
```

- **How verified**: Typed in MCP, value appeared in field
- **Wait for**: Field contains new value
- **Fallback locators**: `get_by_label("Special instructions/requests")`

### Step 7: Click Save Button

- **Action**: Click
- **Target**: Save button in dialog

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `get_by_role("button", name="Save")` | Semantic, unique | None |
| `locator(".btn-save")` | Class-based | Less resilient |

**CHOSEN**: `get_by_role("button", name="Save")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
save_button = outer_iframe.get_by_role("button", name="Save")
save_button.click()

# Wait for dialog to close
dialog_title.wait_for(state="hidden", timeout=10000)

# Verify dialog is closed by checking edit button is visible again
edit_button.wait_for(state="visible", timeout=10000)
```

- **How verified**: Clicked in MCP, dialog closed, changes saved
- **Wait for**: Dialog closes, edit button visible again
- **Fallback locators**: `locator("button:has-text('Save')")`

### Step 8: Verify Changes Were Saved

- **Action**: Re-open dialog and verify field values
- **Target**: Help request and special instructions fields

**VERIFIED PLAYWRIGHT CODE**:
```python
# Open the edit dialog again to verify values
edit_button.click()
dialog_title_verify = outer_iframe.locator("text=Edit property info")
dialog_title_verify.wait_for(state="visible", timeout=10000)

# Verify the help request field has the new value
help_field_verify = outer_iframe.get_by_role("textbox", name="How can we help you?")
expect(help_field_verify).to_have_value(edit_data["help_request"], timeout=5000)

# Verify the special instructions field has the new value
instructions_field_verify = outer_iframe.get_by_role("textbox", name="Special instructions/requests")
expect(instructions_field_verify).to_have_value(edit_data["special_instructions"], timeout=5000)

# Close the dialog
cancel_button = outer_iframe.get_by_role("button", name="Cancel")
cancel_button.click()
dialog_title_verify.wait_for(state="hidden", timeout=10000)
```

- **How verified**: Reopened dialog in MCP, confirmed values match what was entered
- **Wait for**: Dialog opens, values verified, dialog closes

## Context Updates

After successful edit, save to context:
```python
context["edited_help_request"] = edit_data["help_request"]
context["edited_special_instructions"] = edit_data["special_instructions"]
```

## Iframe Handling Notes

vcita uses nested iframes:
1. **Outer iframe**: `iframe[title="angularjs"]` - Contains the edit dialog
2. **Inner iframe**: `#vue_iframe_layout` inside the angularjs iframe - Contains the matter card and edit button

The edit button is in the inner iframe, but the edit dialog appears in the outer iframe.

## Success Verification

- Edit dialog opens successfully
- Both fields are modified with new values
- Save completes without error (dialog closes)
- Re-opening dialog shows the new values persisted
