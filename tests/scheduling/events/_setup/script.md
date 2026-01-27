# Events Setup - Detailed Script

## Objective
Prepare the system for event scheduling tests by creating a group event service and a test client, then navigate to Calendar.

## Initial State
- **Assumes parent (Scheduling) setup has already run**: browser is on Settings > Services page.
- User is logged in (login runs in parent or Step 0 if needed).

## Actions

### Step 0: Login (if needed)
- **Action**: Call function
- **Function**: login
- **Parameters**: None (uses environment variables or config defaults)
- **Expected return**: logged_in_user saved to context

### Step 1: Open New Service Dropdown
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

### Step 2: Select Group Event
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

### Step 3: Fill Service Name
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

### Step 4: Set Max Attendees
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

### Step 5: Select Face to Face Location
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

### Step 6: Select With Fee and Enter Price
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

### Step 7: Click Create
- **Action**: Click
- **Target**: Create button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="Create")` | Unique, semantic | None |
| `iframe.get_by_text("Create")` | Simple | Less semantic |

**CHOSEN**: `iframe.get_by_role("button", name="Create")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE** (updated: wait for create dialog specifically so we don't match the next dialog; then Step 10 handles "I'll do it later"):
```python
import re
# Wait for the create (service) dialog specifically; get_by_role("dialog") matches any dialog,
# so when "Great. Now enter your event dates & times" appears we would never see "hidden".
create_dialog = iframe.get_by_role("dialog", name=re.compile(r"Service info", re.IGNORECASE))
create_btn = iframe.get_by_role("button", name="Create")
create_btn.click()
create_dialog.wait_for(state="hidden", timeout=15000)
```

- **How verified**: Clicked in MCP, group event service created
- **Wait for**: Create dialog closes (then Step 8 handles optional event times dialog)
- **Validation**: After Step 8, setup scrolls the services list (infinite scroll) then asserts the new service name appears (so Schedule Event can find it)

### Step 8: Handle Event Times Dialog (Conditional)
- **Action**: Click (if dialog appears)
- **Target**: "I'll do it later" button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.get_by_role("button", name="I'll do it later")` | Unique, semantic | None |
| `iframe.get_by_text("I'll do it later")` | Simple | Less semantic |

**CHOSEN**: `iframe.get_by_role("button", name="I'll do it later")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE** (HEALED: wait for event-times dialog to close by name):
```python
later_btn = iframe.get_by_role("button", name="I'll do it later")
try:
    later_btn.wait_for(state="visible", timeout=5000)
    later_btn.click()
    iframe.get_by_role("dialog", name=re.compile(r"Great\. Now", re.IGNORECASE)).wait_for(state="hidden", timeout=5000)
except Exception:
    pass
```

- **How verified**: Clicked in MCP when dialog appeared, dialog dismissed
- **Wait for**: Dialog closes (or timeout if dialog doesn't appear)

### Step 8b: Refresh Services List (Navigate Away and Back)
- **Reason**: Known UI issue – the new service does not appear in the list until we navigate away from Services and back. Same workaround as in create_group_event.
- **Action**: Click Settings in sidebar (leave Services), then click Services again in iframe to return.

**VERIFIED PLAYWRIGHT CODE**:
```python
page.get_by_text("Settings", exact=True).click()
page.wait_for_url("**/app/settings**", timeout=10000)
page.wait_for_selector('iframe[title="angularjs"]', state="visible", timeout=5000)
iframe.get_by_role("button", name="Define the services your").click()
page.wait_for_url("**/app/settings/services**", timeout=10000)
iframe.get_by_role("heading", name="Settings / Services").wait_for(state="visible", timeout=10000)
page.wait_for_timeout(500)
```

### Step 9: Save Group Event Service Name
- **Action**: Save name to context (after validating service appears in list)
- **Target**: Context key event_group_service_name

**Validation (after Step 8b)**: Scroll the services list to the end (infinite scroll), then verify the new service appears: `iframe.get_by_text(group_event_name).first.wait_for(state="visible", timeout=20000)`.

**VERIFIED PLAYWRIGHT CODE** (HEALED: after nav-away-and-back, scroll list to end then assert service name):
```python
_scroll_services_list_to_end(page)
page.wait_for_timeout(500)
try:
    iframe.get_by_text(group_event_name).first.wait_for(state="visible", timeout=20000)
except Exception as e:
    raise AssertionError(
        f"Setup could not confirm group event service was created: '{group_event_name}' not found on Services page. "
        "Create dialog closed but service may not have been saved. Check run video/screenshot."
    ) from e
context["event_group_service_name"] = group_event_name
```

- **How verified**: Service name is in list and saved to context
- **Save to context**: event_group_service_name

### Step 10: Create Test Client
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

### Step 11: Navigate to Calendar
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
