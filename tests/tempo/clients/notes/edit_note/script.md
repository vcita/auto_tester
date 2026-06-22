# Edit Note - Detailed Script

## Overview
Edit an existing note on a matter to verify note editing functionality.

## Prerequisites
- User is logged in (parent category _setup)
- Matter exists with `created_matter_id` in context
- Note exists with `created_note_content` in context (from add_note test)

---

## Step 1: Verify Already on Matter Page

- **Action**: Verify URL
- **Target**: Verify browser is already on the matter detail page
- **Expected State**: Browser should be on matter page from previous test (add_note)

**VERIFIED PLAYWRIGHT CODE**:
```python
matter_id = context.get("created_matter_id")
# Verify we're already on the matter page (from previous test)
# Real users don't type URLs - this test runs after add_note which leaves browser here
if matter_id not in page.url:
    raise ValueError(f"Expected to be on matter page {matter_id}, but URL is {page.url}")
page.wait_for_load_state("domcontentloaded")
page.wait_for_timeout(1000)
```

---

## Step 2: Click Notes Tab

- **Action**: Click
- **Target**: Notes tab

**VERIFIED PLAYWRIGHT CODE**:
```python
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
notes_tab = inner_iframe.get_by_role("tab", name="Notes")
notes_tab.click()
page.wait_for_timeout(1000)
```

---

## Step 3: Click on Note to Open Dialog

- **Action**: Click
- **Target**: The note listitem containing our note content

**VERIFIED PLAYWRIGHT CODE**:
```python
original_content = context.get("created_note_content")
note_item = inner_iframe.get_by_role("listitem").filter(has_text=original_content[:30])
note_item.click()
page.wait_for_timeout(1000)
```

- **Wait for**: Note dialog opens showing "Note" title

---

## Step 4: Click on Note Content to Activate Editor

- **Action**: Click
- **Target**: Note content area in the dialog to activate inline editing

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `get_by_role("button").filter(has_text=content)` | Finds the editable button | Works reliably |
| `locator("div").filter(has_text=content)` | Generic | May match multiple |

**CHOSEN**: Filter by original content to find the right button

**VERIFIED PLAYWRIGHT CODE**:
```python
note_content_button = outer_iframe.get_by_role("button").filter(has_text=original_content[:30])
note_content_button.click()
page.wait_for_timeout(500)
```

- **Wait for**: Rich text toolbar appears

---

## Step 5: Clear and Enter New Content

- **Action**: Select all and type new content
- **Target**: The editable note area

**VERIFIED PLAYWRIGHT CODE**:
```python
import time
timestamp = int(time.time())
new_content = f"EDITED: Updated note at {timestamp}"

# Select all and replace
page.keyboard.press("Control+a")
page.keyboard.type(new_content)
page.wait_for_timeout(500)
```

---

## Step 6: Save Changes

- **Action**: Click Save button
- **Target**: Save button in dialog (appears in edit mode)

**VERIFIED PLAYWRIGHT CODE**:
```python
# The dialog shows SAVE button (not Close) when in edit mode
save_button = outer_iframe.get_by_role("button", name="Save")
save_button.click()
page.wait_for_timeout(1500)
```

- **How verified**: Clicked Save in MCP, dialog closed, changes persisted

---

## Step 7: Verify Edit Was Saved

- **Action**: Verify
- **Target**: Updated note appears in list

**VERIFIED PLAYWRIGHT CODE**:
```python
# Verify the edited note appears in list
edited_note = inner_iframe.get_by_role("listitem").filter(has_text="EDITED:")
expect(edited_note).to_be_visible(timeout=10000)
```

---

## Context Updates

```python
context["edited_note_content"] = new_content
```
