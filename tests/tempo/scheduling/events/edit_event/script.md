# Edit Event - Detailed Script

## Objective
Modify details of a scheduled group event instance (e.g., max attendance).

## Initial State
- User is logged in
- A scheduled event exists and is open (context: scheduled_event_id)
- Browser is on event detail page (from view_event or add_attendee test)

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

### Step 2: Click Edit Button
- **Action**: Click
- **Target**: "Edit" button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `outer_iframe.get_by_role("button").filter(has_text="Edit")` | Semantic | May match multiple |
| `outer_iframe.get_by_text("Edit")` | Simple | Less semantic |

**CHOSEN**: `outer_iframe.get_by_role("button").filter(has_text="Edit")` - Semantic button filter.

**VERIFIED PLAYWRIGHT CODE**:
```python
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
edit_btn = outer_iframe.get_by_role('button').filter(has_text='Edit')
edit_btn.click()
# Wait for edit dialog to appear
dialog = outer_iframe.get_by_role('dialog')
dialog.wait_for(state='visible', timeout=10000)
```

- **How verified**: Clicked in MCP, "Edit Event" dialog appeared
- **Wait for**: Dialog with role="dialog" becomes visible
- **Fallback locators**: `outer_iframe.get_by_text("Edit")`

### Step 3: Modify Event Details (Max Attendance)
- **Action**: Click then Fill
- **Target**: Max attendance spinbutton
- **Value**: "12" (increase from 10 to 12)

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `outer_iframe.get_by_role("spinbutton", name="Max attendance *")` | Unique, semantic | None |
| `outer_iframe.get_by_label("Max attendance")` | Simple | Less specific |

**CHOSEN**: `outer_iframe.get_by_role("spinbutton", name="Max attendance *")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Modify max attendance from 10 to 12
max_attendance_field = outer_iframe.get_by_role('spinbutton', name='Max attendance *')
max_attendance_field.click()
max_attendance_field.fill('12')  # fill is OK for number spinbutton
page.wait_for_timeout(500)  # Allow value to be set
```

- **How verified**: Clicked field, filled 12 in MCP, value changed
- **Wait for**: Value is set to 12
- **Fallback locators**: `outer_iframe.get_by_label("Max attendance")`

### Step 4: Click Save
- **Action**: Click
- **Target**: "Save" button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `outer_iframe.get_by_role("button", name="Save")` | Unique, semantic | None |
| `outer_iframe.get_by_text("Save")` | Simple | Less semantic |

**CHOSEN**: `outer_iframe.get_by_role("button", name="Save")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
save_btn = outer_iframe.get_by_role('button', name='Save')
save_btn.click()
# Wait for dialog to close
dialog.wait_for(state='hidden', timeout=10000)
```

- **How verified**: Clicked in MCP, dialog closed, changes saved
- **Wait for**: Dialog closes
- **Fallback locators**: `outer_iframe.get_by_text("Save")`

### Step 5: Verify Changes are Reflected
- **Action**: Verify
- **Target**: Event detail page shows updated max attendance

**VERIFIED PLAYWRIGHT CODE**:
```python
import re
# Wait for page to update
page.wait_for_timeout(2000)  # Allow page to refresh

# Verify max attendance is updated (UI shows "0/12 Registered" in main event detail, in outer iframe)
registered_text = outer_iframe.get_by_text(re.compile(r'\d+\s*/\s*12(\s+Registered)?', re.IGNORECASE))
expect(registered_text).to_be_visible()
```

- **How verified**: Verified max attendance updated in MCP; UI text format may be "0 / 12" or "1 / 12 Registered"; regex allows flexible match.
- **Wait for**: Event detail page shows updated value

## Success Verification
- Event details are updated successfully
- Dialog closes after save
- Changes are visible in the event view (max attendance shows "/ 12 Registered")
- Event still appears in calendar at correct time
