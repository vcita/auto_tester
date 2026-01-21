# Add Note - Detailed Script

## Overview
Add a note to an existing matter to verify note creation functionality.

## Prerequisites
- User is logged in (parent category _setup)
- Matter exists with `created_matter_id` in context

---

## Step 1: Verify Already on Matter Page

- **Action**: Verify URL
- **Target**: Verify browser is already on the matter detail page
- **Expected State**: Browser should be on matter page from previous test (edit_contact)

**VERIFIED PLAYWRIGHT CODE**:
```python
matter_id = context.get("created_matter_id")
# Verify we're already on the matter page (from previous test)
# Real users don't type URLs - this test runs after edit_contact which leaves browser here
if matter_id not in page.url:
    raise ValueError(f"Expected to be on matter page {matter_id}, but URL is {page.url}")
page.wait_for_load_state("domcontentloaded")
page.wait_for_timeout(1000)
```

- **Wait for**: Page is ready (already loaded from previous test)

---

## Step 2: Click Notes Tab

- **Action**: Click
- **Target**: Notes tab in the tablist

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `get_by_role("tab", name="Notes")` | Semantic, accessible | Needs iframe context |
| `locator('[role="tab"]').filter(has_text="Notes")` | Works | Less semantic |

**CHOSEN**: `get_by_role("tab", name="Notes")` - Semantic selector using role

**VERIFIED PLAYWRIGHT CODE**:
```python
outer_iframe = page.frame_locator('iframe[title="angularjs"]')
inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
notes_tab = inner_iframe.get_by_role("tab", name="Notes")
notes_tab.click()
page.wait_for_timeout(1000)
```

- **Wait for**: Notes tab becomes selected

---

## Step 3: Click Add Note Button

- **Action**: Click
- **Target**: "Add note" button in header

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `get_by_role("button", name="Add note")` | Semantic, exact name | In outer iframe |
| `locator("button").filter(has_text="Add note")` | Works | Less specific |

**CHOSEN**: `get_by_role("button", name="Add note")` - Clean semantic locator

**VERIFIED PLAYWRIGHT CODE**:
```python
add_note_button = outer_iframe.get_by_role("button", name="Add note")
add_note_button.click()
page.wait_for_timeout(1000)
```

- **Wait for**: "New note" dialog opens

---

## Step 4: Enter Note Content

- **Action**: Type
- **Target**: Rich text editor in the note dialog
- **Value**: Test note content with timestamp

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `locator("#tiny-vue_...")` | Direct ID | ID has dynamic component |
| `get_by_text("Add your note here")` | Matches placeholder | May not be editable directly |
| Click on text area then fill | Works reliably | Multi-step |

**CHOSEN**: Click on the contenteditable area then use keyboard.type() - Rich text editors require click to focus, then keyboard input

**VERIFIED PLAYWRIGHT CODE**:
```python
import time
timestamp = int(time.time())
note_content = f"Automated test note - Created at {timestamp}"

wizard_iframe = outer_iframe.frame_locator('#vue_wizard_iframe')
# Rich text editor - use contenteditable locator with fallback to placeholder text
note_area = wizard_iframe.locator('div[contenteditable="true"]').or_(
    wizard_iframe.get_by_text("Add your note here")
)
note_area.first.click()
page.wait_for_timeout(500)

# Use keyboard.type() for rich text editors (not fill() or press_sequentially())
page.keyboard.type(note_content)
page.wait_for_timeout(500)
```

- **How verified**: Clicked in MCP, note content appeared character by character
- **Wait for**: Note content appears in editor
- **Note**: Rich text editors (contenteditable) require `keyboard.type()`, not `fill()` or `press_sequentially()`

---

## Step 5: Save Note

- **Action**: Click
- **Target**: Save button in dialog

**VERIFIED PLAYWRIGHT CODE**:
```python
save_button = wizard_iframe.get_by_role("button", name="Save")
save_button.click()
page.wait_for_timeout(2000)
```

- **Wait for**: Toast "Note added successfully" appears

---

## Step 6: Verify Note Created

- **Action**: Verify
- **Target**: Note appears in notes list

**VERIFIED PLAYWRIGHT CODE**:
```python
# Verify note appears in the list
note_item = inner_iframe.get_by_role("listitem").filter(has_text=note_content[:30])
expect(note_item).to_be_visible(timeout=10000)
```

---

## Context Updates

```python
context["created_note_content"] = note_content
```
