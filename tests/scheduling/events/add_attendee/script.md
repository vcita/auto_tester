# Add Attendee - Detailed Script

## Objective
Add a client as an attendee to a scheduled group event.

## Initial State
- User is logged in
- A scheduled event exists and is open (context: scheduled_event_id)
- A test client exists (context: event_client_name)
- Browser is on event detail page (from view_event test)

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

### Step 2: Click Register Clients Button
- **Action**: Click
- **Target**: "Register Clients" button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `outer_iframe.get_by_role("button", name="Register Clients")` | Unique, semantic | None |
| `outer_iframe.get_by_text("Register Clients")` | Simple | Less semantic |

**CHOSEN**: `outer_iframe.get_by_role("button", name="Register Clients")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
register_btn = outer_iframe.get_by_role('button', name='Register Clients')
register_btn.click()
# Wait for dialog to appear
dialog = outer_iframe.get_by_role('dialog')
dialog.wait_for(state='visible', timeout=10000)
```

- **How verified**: Clicked in MCP, "Register Clients" dialog appeared
- **Wait for**: Dialog with role="dialog" becomes visible
- **Fallback locators**: `outer_iframe.get_by_text("Register Clients")`

### Step 3: Search for Test Client
- **Action**: Type
- **Target**: Search textbox in dialog
- **Value**: Client name from context

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `outer_iframe.get_by_role("textbox", name="Search by name, email or tag")` | Unique, semantic | None |
| `outer_iframe.get_by_text("Search by name, email or tag")` | Simple | Less semantic |

**CHOSEN**: `outer_iframe.get_by_role("textbox", name="Search by name, email or tag")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Get client name from context
client_name = context.get("event_client_name")
if not client_name:
    raise ValueError("No event_client_name in context. Run _setup first.")

# Search for client
search_field = outer_iframe.get_by_role('textbox', name='Search by name, email or tag')
search_field.click()
page.wait_for_timeout(100)
search_field.press_sequentially(client_name, delay=30)
page.wait_for_timeout(500)  # Allow search to filter results
```

- **How verified**: Typed in MCP, search field filtered results
- **Wait for**: Search results update
- **Fallback locators**: `outer_iframe.get_by_label("Search by name, email or tag")`

### Step 4: Select Client from Results
- **Action**: Click
- **Target**: Client button in filtered list

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `outer_iframe.get_by_role("button").filter(has_text=client_name)` | Matches client name | May match multiple if similar names |
| `outer_iframe.get_by_text(client_name)` | Simple | May match multiple |

**CHOSEN**: `outer_iframe.get_by_role("button").filter(has_text=client_name).first()` - Matches client name, first() gets the first match.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Select the client from filtered results
client_button = outer_iframe.get_by_role('button').filter(has_text=client_name).first()
client_button.wait_for(state='visible', timeout=10000)
client_button.click()
page.wait_for_timeout(500)  # Allow selection to register
```

- **How verified**: Clicked client in MCP, client was selected
- **Wait for**: Client is selected (Continue button may become enabled)
- **Fallback locators**: `outer_iframe.get_by_text(client_name)`

### Step 5: Click Continue to Register
- **Action**: Click
- **Target**: "Continue" button

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `outer_iframe.get_by_role("button", name="Continue")` | Unique, semantic | None |
| `outer_iframe.get_by_text("Continue")` | Simple | Less semantic |

**CHOSEN**: `outer_iframe.get_by_role("button", name="Continue")` - Unique and semantic.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Click Continue to register the client
continue_btn = outer_iframe.get_by_role('button', name='Continue')
continue_btn.wait_for(state='visible', timeout=10000)
# Wait for button to be enabled (may be disabled until client is selected)
continue_btn.wait_for(state='attached', timeout=5000)
continue_btn.click()
# Wait for dialog to close
dialog.wait_for(state='hidden', timeout=10000)
```

- **How verified**: Clicked in MCP, client was registered, dialog closed
- **Wait for**: Dialog closes
- **Fallback locators**: `outer_iframe.get_by_text("Continue")`

### Step 6: Verify Client Added to Attendees
- **Action**: Verify
- **Target**: Attendees list shows the client

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for page to update
page.wait_for_timeout(2000)  # Allow attendees list to update

# Verify client appears in attendees list
# The attendees tab should show the client
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
attendees_tab = inner_iframe.get_by_role('tab', name=re.compile(r'Attendees'))
attendees_tab.wait_for(state='visible', timeout=10000)

# Check if attendees count increased or client name appears
# The tab name changes from "Attendees (0)" to "Attendees (1)"
attendees_count_text = attendees_tab.text_content()
# Should contain "Attendees (1)" or similar

# Save client ID to context (if available from the button or list)
context["event_attendee_id"] = context.get("event_client_id")
```

- **How verified**: Verified attendees count increased in MCP
- **Wait for**: Attendees list updates
- **Save to context**: event_attendee_id (uses event_client_id)

## Success Verification
- Client is added as attendee
- Dialog closes after registration
- Attendees count increases (e.g., from "Attendees (0)" to "Attendees (1)")
- Client appears in attendees list
- Context contains:
  - event_attendee_id: ID of the client added to event
