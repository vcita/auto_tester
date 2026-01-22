# Scheduling Setup - Detailed Script

## Overview
Login and navigate to Settings > Services page to prepare for service management tests.

## Prerequisites
- vcita account credentials configured

---

## Step 1: Login

- **Action**: Call function
- **Function**: login
- **Parameters**: username, password from config

**VERIFIED PLAYWRIGHT CODE**:
```python
from tests._functions.login.test import fn_login
fn_login(page, context, username=username, password=password)
```

- **Wait for**: Dashboard loads
- **Context**: `logged_in_user` saved by login function

---

## Step 2: Navigate to Settings

- **Action**: Click
- **Target**: Settings menu item in sidebar

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `page.getByText('Settings')` | Simple, matches visible text | May match multiple elements |
| `page.locator('.menu-items-group').getByText('Settings')` | More specific | Depends on class names |

**CHOSEN**: `page.getByText('Settings')` - Direct text match, verified working in MCP

**VERIFIED PLAYWRIGHT CODE**:
```python
page.get_by_text('Settings').click()
page.wait_for_url("**/app/settings**")
page.wait_for_timeout(1000)
```

- **How verified**: Clicked in MCP, navigated to Settings page
- **Wait for**: URL contains "/app/settings"

---

## Step 3: Navigate to Services

- **Action**: Click
- **Target**: Services button in Settings page (inside iframe)

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `iframe.getByRole('button', { name: 'Define the services your' })` | Semantic, unique | Long name |
| `iframe.getByRole('heading', { name: 'Services' })` | Clear name | Heading not clickable |
| `iframe.getByText('Services').first` | Simple | May match category label |

**CHOSEN**: `iframe.getByRole('button', { name: 'Define the services your' })` - Button is unique with its description text

**VERIFIED PLAYWRIGHT CODE**:
```python
# Wait for iframe to load
page.wait_for_selector('iframe[title="angularjs"]', timeout=15000)
page.wait_for_timeout(1000)

# Get iframe and click Services
iframe = page.frame_locator('iframe[title="angularjs"]')
services_button = iframe.get_by_role("button", name="Define the services your")
services_button.click()
page.wait_for_url("**/app/settings/services**")
page.wait_for_timeout(1000)
```

- **How verified**: Clicked in MCP, navigated to Services page
- **Wait for**: URL contains "/app/settings/services"
- **Fallback locators**: `iframe.locator('text=Services').nth(1)`

---

## Step 4: Verify Services Page Loaded

- **Action**: Verify
- **Target**: Services page heading

**VERIFIED PLAYWRIGHT CODE**:
```python
# Verify we're on the Services page
heading = iframe.get_by_role("heading", name="Settings / Services")
expect(heading).to_be_visible(timeout=10000)
```

- **How verified**: Heading visible in MCP snapshot
- **Wait for**: "Settings / Services" heading is visible

---

## Success Verification
- URL contains "/app/settings/services"
- "Settings / Services" heading is visible
- "New service" button is visible
