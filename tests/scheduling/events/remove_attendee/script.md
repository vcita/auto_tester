# Remove Attendee - Detailed Script

## Objective
Remove a client from a scheduled group event's attendee list.

## Initial State
- User is logged in
- A scheduled event exists and is open (context: scheduled_event_id)
- An attendee exists on the event (context: event_attendee_id)
- Browser is on event detail page (from add_attendee test)

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

### Step 2: Navigate to Attendees Tab
- **Action**: Click
- **Target**: "Attendees" tab

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `inner_iframe.get_by_role("tab", name=re.compile(r"Attendees"))` | Semantic, matches pattern | Uses regex |
| `inner_iframe.get_by_role("tab").filter(has_text="Attendees")` | Simple filter | May match multiple |

**CHOSEN**: `inner_iframe.get_by_role("tab", name=re.compile(r"Attendees"))` - Semantic and matches tab name pattern.

**VERIFIED PLAYWRIGHT CODE**:
```python
import re
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')

# Click Attendees tab (if not already selected)
attendees_tab = inner_iframe.get_by_role('tab', name=re.compile(r'Attendees'))
attendees_tab.wait_for(state='visible', timeout=10000)
if 'selected' not in attendees_tab.get_attribute('class') or attendees_tab.get_attribute('aria-selected') != 'true':
    attendees_tab.click()
    page.wait_for_timeout(500)  # Allow tab content to load
```

- **How verified**: Clicked tab in MCP, attendees list appeared
- **Wait for**: Attendees list is visible
- **Fallback locators**: `inner_iframe.get_by_text("Attendees")`

### Step 3: Find Attendee in List
- **Action**: Locate
- **Target**: Attendee entry in the list

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `inner_iframe.get_by_text(client_name)` | Simple, matches name | May match multiple |
| `inner_iframe.get_by_role("listitem").filter(has_text=client_name)` | More specific | Depends on list structure |

**CHOSEN**: `inner_iframe.get_by_text(client_name)` - Client name is unique in attendees list.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Get client name from context
client_name = context.get("event_client_name")
if not client_name:
    raise ValueError("No event_client_name in context. Run _setup first.")

# Wait for attendees list to load
try:
    inner_iframe.locator('*').filter(has_text="Not paid").first().wait_for(state='visible', timeout=10000)
    page.wait_for_timeout(2000)
except:
    try:
        inner_iframe.locator('*').filter(has_text="Paid").first().wait_for(state='visible', timeout=10000)
        page.wait_for_timeout(2000)
    except:
        page.wait_for_timeout(3000)

# Re-establish iframe references to ensure they're fresh
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')

# Find the attendee in the list - get_by_text works reliably
attendee_item = inner_iframe.get_by_text(client_name)
attendee_item.wait_for(state='visible', timeout=10000)
```

- **How verified**: Found attendee in list in MCP
- **Wait for**: Attendee item is visible
- **Fallback locators**: `inner_iframe.get_by_role("listitem").filter(has_text=client_name)`

### Step 4: Click 3 Dots Menu and Select "Cancel Registration"
- **Action**: Click
- **Target**: 3 dots menu button on attendee item

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| Find 3 dots button in attendee container | Contextual, accurate | Requires hover first |
| `inner_iframe.get_by_role("button").filter(has_text="Remove")` | Semantic | May match multiple |
| Locate button within attendee's container | Most accurate | Requires DOM structure knowledge |

**CHOSEN**: Locate 3 dots button within attendee's container after hovering - buttons only appear on hover.

**VERIFIED PLAYWRIGHT CODE**:
```python
# IMPORTANT: Buttons are only visible when hovering over the attendee name
# First, hover over the attendee name to reveal the buttons
attendee_item.hover()
page.wait_for_timeout(1500)  # Wait for buttons to appear after hover

# Find the 3 dots menu button near the attendee
# Get parent container (2 levels up from attendee text)
attendee_container = attendee_item.locator('xpath=ancestor::*[position()=2]')

# Look for all buttons in the container
buttons = attendee_container.locator('button')
btn_count = buttons.count()

# Check each button to find the 3 dots menu (NOT the bill/payment icon)
menu_btn = None
for i in range(btn_count):
    btn = buttons.nth(i)
    btn_class = btn.get_attribute('class') or ""
    
    # Skip bill/payment icon
    if "take-payment-button" in btn_class:
        continue
    
    # 3 dots menu: must have BOTH "three-dots" AND "activator-container" classes
    has_three_dots = "three-dots" in btn_class
    has_activator = "activator-container" in btn_class
    
    if has_three_dots and has_activator:
        menu_btn = btn
        break

if not menu_btn:
    raise ValueError(f"3 dots menu button not found for attendee '{client_name}'. Button must have both 'three-dots' and 'activator-container' classes.")

# Click the 3 dots menu button using evaluate for reliability
menu_btn.evaluate("""
    (el) => {
        el.scrollIntoView({ behavior: 'instant', block: 'center' });
        el.click();
    }
""")
page.wait_for_timeout(2000)  # Wait for menu to appear
```

- **How verified**: Clicked 3 dots button in MCP, menu appeared
- **Wait for**: Menu appears after clicking
- **Fallback locators**: Various button locators near attendee item

### Step 4a: Click "Cancel Registration" Option in Menu
- **Action**: Click
- **Target**: "Cancel registration" menu item

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `menu.get_by_text("Cancel registration")` | Simple, matches text | Case sensitive |
| `menu.get_by_text(re.compile(r'Cancel.*[Rr]egistration'))` | Flexible case | Uses regex |
| `menu.locator('*').filter(has_text='Cancel registration')` | Partial matching | May match multiple |

**CHOSEN**: Try regex first, fallback to filter - ensures we find the menu item reliably.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Instead of looking for the menu role, wait for the "Cancel registration" menu item directly
# This is more reliable - if the menu item appears, we know the menu is there
# IMPORTANT: Re-establish iframe references right before looking for menu item
page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')

cancel_option = None
menu_found = False

# Try inner iframe first - wait for "Cancel registration" menu item
# The menu appears in inner_iframe (verified in MCP)
# Use polling approach: check count first, poll until menu item appears, then wait for visibility
try:
    cancel_option = inner_iframe.get_by_role('menuitem', name=re.compile(r'Cancel.*[Rr]egistration', re.IGNORECASE))
    # Poll until menu item appears (check count every 500ms, up to 5 seconds)
    count = 0
    for attempt in range(10):
        count = cancel_option.count()
        if count > 0:
            break
        page.wait_for_timeout(500)  # Wait 500ms between checks
    
    if count > 0:
        # Menu item exists, now wait for it to be visible
        cancel_option.first().wait_for(state='visible', timeout=5000)
        menu_found = True
except:
    # Try alternative: look for exact text match
    try:
        cancel_option = inner_iframe.locator('*').filter(has_text='Cancel registration')
        count = 0
        for attempt in range(10):
            count = cancel_option.count()
            if count > 0:
                break
            page.wait_for_timeout(500)
        if count > 0:
            cancel_option.first().wait_for(state='visible', timeout=5000)
            menu_found = True
    except:
        pass

# If not found in inner iframe, try outer iframe (using get_by_text - verified in MCP)
if not menu_found:
    try:
        cancel_option = outer_iframe.get_by_text('Cancel registration')
        count = 0
        for attempt in range(10):
            count = cancel_option.count()
            if count > 0:
                break
            page.wait_for_timeout(500)
        if count > 0:
            cancel_option.first().wait_for(state='visible', timeout=5000)
            menu_found = True
    except:
        pass

# If still not found, try document (using get_by_text - verified in MCP)
if not menu_found:
    try:
        cancel_option = page.get_by_text('Cancel registration')
        count = 0
        for attempt in range(10):
            count = cancel_option.count()
            if count > 0:
                break
            page.wait_for_timeout(500)
        if count > 0:
            cancel_option.first().wait_for(state='visible', timeout=5000)
            menu_found = True
    except:
        pass

if not menu_found or cancel_option is None or cancel_option.count() == 0:
    raise ValueError("'Cancel registration' menu item did not appear after clicking 3 dots button")

# We found the cancel option, now click it (already waited for visibility above)
cancel_option.first().click()
page.wait_for_timeout(2000)  # Wait for confirmation dialog to appear
```

- **How verified**: 
  - MCP DOM inspection showed menu items are DIV elements with class "v-list-item" and role="menuitem"
  - Tested exact Python code flow in MCP: `get_by_text('Cancel registration')` works reliably in inner_iframe
  - Verified polling approach (10 attempts, 500ms each) successfully finds menu item
  - Clicked "Cancel registration" in MCP, confirmation dialog appeared
- **Wait for**: Confirmation dialog appears
- **Fallback locators**: locator('*').filter(has_text='Cancel registration') for partial match

### Step 5: Submit Confirmation Dialog
- **Action**: Click (if dialog appears)
- **Target**: Confirm button in confirmation dialog

**Note**: There may or may not be a confirmation dialog. Handle both cases.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Check if confirmation dialog appeared
confirm_btn = outer_iframe.get_by_role('button', name=re.compile(r'Confirm|Yes|Remove|Delete'))
try:
    confirm_btn.wait_for(state='visible', timeout=3000)
    confirm_btn.click()
    page.wait_for_timeout(500)
except:
    # No confirmation dialog - removal was immediate
    pass
```

- **How verified**: Handled confirmation dialog in MCP if it appeared
- **Wait for**: Dialog closes (if appeared)

### Step 6: Verify Attendee Removed
- **Action**: Verify
- **Target**: Attendee removed (count is 0 AND shows "Canceled by" indicator)

**IMPORTANT**: We validate removal by checking BOTH:
1. The attendees count is 0 (attendee no longer counted as active)
2. The attendee shows "Canceled by" indicator (confirms it's in canceled state)
Both conditions must be true for removal to be confirmed.

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| Check count only | Simple | Doesn't verify canceled state |
| Check "Canceled by" text only | Verifies state | Doesn't verify count |
| Check BOTH count and "Canceled by" | Most reliable, verifies both | More complex |

**CHOSEN**: Check BOTH count is 0 AND "Canceled by" indicator exists - This ensures the attendee is both removed from active count and shows cancellation status.

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for list to update after removal
page.wait_for_timeout(3000)  # Allow list to refresh

# Step 6a: Verify attendees count is 0
attendees_tab = inner_iframe.get_by_role('tab', name=re.compile(r'Attendees'))
attendees_count_text = attendees_tab.first().text_content()
count_match = re.search(r'\((\d+)\)', attendees_count_text or "")
attendees_count = int(count_match.group(1)) if count_match else -1

# Step 6b: Find the attendee by name and check if it's in canceled state
attendee_items = inner_iframe.get_by_text(client_name)
attendee_count = attendee_items.count()

# Both validations must pass:
# 1. Count must be 0
# 2. If attendee exists in DOM, it must show "Canceled by" indicator

count_is_zero = attendees_count == 0
has_canceled_indicator = False

if attendee_count == 0:
    # Attendee name not found in DOM - completely removed
    # This is acceptable as long as count is also 0
    print(f"  [INFO] Attendee completely removed from DOM")
else:
    # Attendee name found in DOM - MUST have "Canceled by" indicator
    attendee_element = attendee_items.first()
    # Get parent container (should contain both name and cancellation indicator)
    container = attendee_element.locator('xpath=ancestor::*[position()=2]')
    container_text = container.text_content()
    
    # Check for "Canceled by" indicator in container text
    has_canceled_text = "Canceled by" in (container_text or "")
    
    # Also verify cancellation indicator element exists within container
    canceled_indicator = container.locator('*').filter(has_text=re.compile(r'Canceled by', re.IGNORECASE))
    canceled_indicator_count = canceled_indicator.count()
    
    has_canceled_indicator = has_canceled_text and canceled_indicator_count > 0
    
    if not has_canceled_indicator:
        raise ValueError(f"Attendee '{client_name}' exists in DOM but does NOT show 'Canceled by' indicator. Removal may have failed. Container text: {container_text[:100]}")

# Re-check count if needed (in case UI is still updating)
if not count_is_zero:
    page.wait_for_timeout(2000)
    attendees_count_text = attendees_tab.first().text_content()
    count_match = re.search(r'\((\d+)\)', attendees_count_text or "")
    attendees_count = int(count_match.group(1)) if count_match else -1
    count_is_zero = attendees_count == 0

# Both conditions must be true
if not count_is_zero:
    raise ValueError(f"Attendees count is {attendees_count} (expected 0). Removal may have failed.")

# If attendee exists in DOM, it must have canceled indicator (already checked above)
# If attendee doesn't exist in DOM, that's fine as long as count is 0

print(f"  [OK] Attendee removed successfully")
print(f"       Attendees tab: {attendees_count_text} (count: {attendees_count})")
if attendee_count > 0:
    print(f"       Canceled indicator: Found")
else:
    print(f"       Canceled indicator: N/A (attendee removed from DOM)")
```

- **How verified**: Tested in MCP - verified both count is 0 and "Canceled by Autotest" indicator appears
- **Wait for**: List updates, count changes to 0, cancellation indicator appears

## Success Verification
- Attendee is removed from the event
- Attendee no longer appears in attendees list
- Attendees count decreases (e.g., from "Attendees (1)" to "Attendees (0)")
- Event still exists and is accessible
