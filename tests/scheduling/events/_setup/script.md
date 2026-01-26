# Events Setup - Detailed Script

## Objective
Prepare the system for event scheduling tests by creating a group event service and a test client, then navigate to Calendar.

## Initial State
- User may or may not be logged in
- Browser may be on any page

## Actions

### Step 0: Login (if needed)
- **Action**: Call function
- **Function**: login
- **Parameters**: None (uses environment variables or config defaults)
- **Expected return**: logged_in_user saved to context

### Step 1: Navigate to Settings
- **Action**: Click
- **Target**: Settings menu item in sidebar

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `get_by_text("Settings", exact=True)` | Simple, readable | May match multiple elements |
| `locator("div").filter({ hasText: /^Settings$/ })` | More specific | Less semantic |

**CHOSEN**: `get_by_text("Settings", exact=True)` - Unique menu item in sidebar.

**VERIFIED PLAYWRIGHT CODE**:
```python
settings_menu = page.get_by_text("Settings", exact=True)
settings_menu.click()
page.wait_for_url("**/app/settings**", timeout=10000)
```

- **How verified**: Clicked in MCP, navigated to Settings page
- **Wait for**: URL contains "/app/settings"
- **Fallback locators**: `locator("div").filter({ hasText: /^Settings$/ })`

### Step 2: Navigate to Services
- **Action**: Click
- **Target**: Services button in Settings page

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="Define the services your")` | Semantic, accessible | Long name |
| `iframe.get_by_text("Services")` | Short | May match multiple elements |

**CHOSEN**: `iframe.get_by_role("button", name="Define the services your")` - Unique button with accessible name.

**VERIFIED PLAYWRIGHT CODE**:
```python
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
iframe = page.frame_locator('iframe[title="angularjs"]')
services_btn = iframe.get_by_role("button", name="Define the services your")
services_btn.click()
page.wait_for_url("**/app/settings/services**", timeout=10000)
```

- **How verified**: Clicked in MCP, navigated to Services page
- **Wait for**: URL contains "/app/settings/services"
- **Fallback locators**: `iframe.get_by_text("Services")`

### Step 3: Open New Service Dropdown
- **Action**: Click
- **Target**: "New service" dropdown button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="New service icon-caret-down")` | Exact match | Includes icon name |
| `iframe.get_by_role("button", name="New service")` | Simpler | May not be unique |

**CHOSEN**: `iframe.get_by_role("button", name="New service icon-caret-down")` - Exact accessible name.

**VERIFIED PLAYWRIGHT CODE**:
```python
new_service_btn = iframe.get_by_role("button", name="New service icon-caret-down")
new_service_btn.click()
# Wait for dropdown menu to appear
menu = iframe.get_by_role("menu")
menu.wait_for(state="visible", timeout=5000)
```

- **How verified**: Clicked in MCP, dropdown menu appeared
- **Wait for**: Menu with role="menu" becomes visible
- **Fallback locators**: `iframe.get_by_role("button").filter(has_text="New service")`

### Step 4: Select Group Event
- **Action**: Click
- **Target**: "Group event" menu item

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("menuitem", name="Group event")` | Semantic, unique | None |
| `iframe.get_by_text("Group event")` | Simple | Less semantic |

**CHOSEN**: `iframe.get_by_role("menuitem", name="Group event")` - Semantic and unique.

**VERIFIED PLAYWRIGHT CODE**:
```python
group_event_option = iframe.get_by_role("menuitem", name="Group event")
group_event_option.click()
# Wait for dialog to appear
dialog = iframe.get_by_role("dialog")
dialog.wait_for(state="visible", timeout=10000)
```

- **How verified**: Clicked in MCP, dialog for creating group event appeared
- **Wait for**: Dialog with role="dialog" becomes visible
- **Fallback locators**: `iframe.get_by_text("Group event")`

### Step 5: Fill Service Name
- **Action**: Type
- **Target**: Service name textbox
- **Value**: "Event Test Workshop {timestamp}"

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("textbox", name="Service name *")` | Semantic, accessible | None |
| `iframe.get_by_label("Service name")` | Simple | May match multiple |

**CHOSEN**: `iframe.get_by_role("textbox", name="Service name *")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
timestamp = int(time.time())
group_event_name = f"Event Test Workshop {timestamp}"
name_field = iframe.get_by_role("textbox", name="Service name *")
name_field.click()
page.wait_for_timeout(100)  # Brief delay for field focus
name_field.press_sequentially(group_event_name, delay=30)
```

- **How verified**: Typed in MCP, value appeared character by character
- **Wait for**: Field is focused and ready
- **Fallback locators**: `iframe.get_by_label("Service name")`

### Step 6: Set Max Attendees
- **Action**: Fill
- **Target**: Max attendees spinbutton
- **Value**: "10"

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")` | Exact match | Includes icon name |
| `iframe.get_by_role("spinbutton", name="Max attendees")` | Simpler | May not be unique |

**CHOSEN**: `iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")` - Exact accessible name.

**VERIFIED PLAYWRIGHT CODE**:
```python
max_attendees_field = iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")
max_attendees_field.click()
max_attendees_field.fill("10")  # fill is OK for number spinbutton
```

- **How verified**: Filled in MCP, value set to 10
- **Wait for**: Value is set
- **Fallback locators**: `iframe.get_by_label("Max attendees")`

### Step 7: Select Face to Face Location
- **Action**: Click
- **Target**: "Face to face" location button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="icon-Home Face to face")` | Exact match | Includes icon name |
| `iframe.get_by_text("Face to face")` | Simpler | May match multiple |

**CHOSEN**: `iframe.get_by_role("button", name="icon-Home Face to face")` - Exact accessible name.

**VERIFIED PLAYWRIGHT CODE**:
```python
face_to_face_btn = iframe.get_by_role("button", name="icon-Home Face to face")
face_to_face_btn.click()
# Wait for address options to appear
address_options = iframe.get_by_role("radiogroup")
address_options.wait_for(state="visible", timeout=5000)
# Default "My business address" is already selected - no action needed
```

- **How verified**: Clicked in MCP, address options appeared
- **Wait for**: Radiogroup with address options becomes visible
- **Fallback locators**: `iframe.get_by_text("Face to face")`

### Step 8: Select With Fee and Enter Price
- **Action**: Click then Fill
- **Target**: "With fee" button, then price spinbutton
- **Value**: "25"

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="icon-Credit-card With fee")` | Exact match | Includes icon name |
| `iframe.get_by_text("With fee")` | Simpler | May match multiple |

**CHOSEN**: `iframe.get_by_role("button", name="icon-Credit-card With fee")` - Exact accessible name.

**VERIFIED PLAYWRIGHT CODE**:
```python
with_fee_btn = iframe.get_by_role("button", name="icon-Credit-card With fee")
with_fee_btn.click()
# Wait for price field to appear
price_field = iframe.get_by_role("spinbutton", name="Service price *")
price_field.wait_for(state="visible", timeout=5000)
price_field.click()
price_field.fill("25")  # fill is OK for number spinbutton
```

- **How verified**: Clicked "With fee" in MCP, price field appeared, filled 25
- **Wait for**: Price field becomes visible
- **Fallback locators**: `iframe.get_by_text("With fee")`

### Step 9: Click Create
- **Action**: Click
- **Target**: Create button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="Create")` | Unique, semantic | None |
| `iframe.get_by_text("Create")` | Simple | Less semantic |

**CHOSEN**: `iframe.get_by_role("button", name="Create")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE** (updated: validate creation — wait for dialog to close, then verify service in list):
```python
create_dialog = iframe.get_by_role("dialog")
create_btn = iframe.get_by_role("button", name="Create")
create_btn.click()
# Validate creation flow: wait for create dialog to close (fails if Create failed)
create_dialog.wait_for(state="hidden", timeout=15000)
```

- **How verified**: Clicked in MCP, group event service created
- **Wait for**: Create dialog closes (then Step 10 handles optional event times dialog)
- **Validation**: After Step 10, setup asserts the new service name appears on the Services page (so Schedule Event can find it)

### Step 10: Handle Event Times Dialog (Conditional)
- **Action**: Click (if dialog appears)
- **Target**: "I'll do it later" button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="I'll do it later")` | Unique, semantic | None |
| `iframe.get_by_text("I'll do it later")` | Simple | Less semantic |

**CHOSEN**: `iframe.get_by_role("button", name="I'll do it later")` - Unique and semantic.

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

- **How verified**: Clicked in MCP when dialog appeared, dialog dismissed
- **Wait for**: Dialog closes (or timeout if dialog doesn't appear)
- **Fallback locators**: `iframe.get_by_text("I'll do it later")`

### Step 11: Save Group Event Service Name
- **Action**: Save name to context (after validating service appears in list)
- **Target**: Context key event_group_service_name

**Validation (after Step 10)**: Before saving, setup verifies the new service appears on the Services page: `iframe.get_by_text(group_event_name).first.wait_for(state="visible", timeout=10000)`. If not found, setup fails with a clear error so we don't assume creation succeeded.

**VERIFIED PLAYWRIGHT CODE**:
```python
# After event times dialog handling: verify service is in the list
try:
    iframe.get_by_text(group_event_name).first.wait_for(state="visible", timeout=10000)
except Exception as e:
    raise AssertionError(
        f"Setup could not confirm group event service was created: '{group_event_name}' not found on Services page. "
        "Create dialog closed but service may not have been saved. Check run video/screenshot."
    ) from e

context["event_group_service_name"] = group_event_name
```

- **How verified**: Service name is in list and saved to context
- **Save to context**: event_group_service_name

### Step 12: Create Test Client
- **Action**: Call function
- **Function**: create_client
- **Parameters**:
  - first_name: "Event"
  - last_name: "TestClient{timestamp}"
- **Expected return**: created_client_id, created_client_name, created_client_email saved to context

**VERIFIED PLAYWRIGHT CODE**:
```python
from tests._functions.create_client.test import fn_create_client

timestamp = int(time.time())
fn_create_client(
    page, 
    context, 
    first_name="Event",
    last_name=f"TestClient{timestamp}"
)

# Save to context with event-specific names
context["event_client_id"] = context.get("created_client_id")
context["event_client_name"] = context.get("created_client_name")
context["event_client_email"] = context.get("created_client_email")
```

- **How verified**: Function call creates client successfully
- **Wait for**: Client detail page loads
- **Save to context**: event_client_id, event_client_name, event_client_email

### Step 13: Navigate to Calendar
- **Action**: Click
- **Target**: Calendar menu item

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `page.get_by_text("Calendar", exact=True)` | Simple, unique | None |
| `page.get_by_role("button", name="Calendar")` | Semantic | May not be button |

**CHOSEN**: `page.get_by_text("Calendar", exact=True)` - Unique menu item.

**VERIFIED PLAYWRIGHT CODE**:
```python
calendar_menu = page.get_by_text("Calendar", exact=True)
calendar_menu.click()
page.wait_for_url("**/app/calendar**", timeout=10000)
```

- **How verified**: Clicked in MCP, navigated to Calendar page
- **Wait for**: URL contains "/app/calendar"
- **Fallback locators**: `page.get_by_role("button", name="Calendar")`

## Success Verification
- Group event service is created (name saved to context)
- Test client is created (ID in context)
- Browser is on Calendar page
- Context contains:
  - event_group_service_name: Name of the group event service
  - event_client_id: ID of the test client
  - event_client_name: Full name of the test client
  - event_client_email: Email of the test client
