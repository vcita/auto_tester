# Delete Note - Detailed Script

## Overview
Delete a note from a matter to verify note deletion functionality.

## Prerequisites
- User is logged in (parent category _setup)
- Matter exists with `created_matter_id` in context
- Note exists with `edited_note_content` in context (from edit_note test)

---

## Step 1: Verify Already on Matter Page

- **Action**: Verify URL
- **Target**: Verify browser is already on the matter detail page
- **Expected State**: Browser should be on matter page from previous test (edit_note)

**VERIFIED PLAYWRIGHT CODE**:
```python
matter_id = context.get("created_matter_id")
# Verify we're already on the matter page (from previous test)
# Real users don't type URLs - this test runs after edit_note which leaves browser here
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

## Step 3: Hover Over Note and Click Three Dots Menu

- **Action**: Click on three dots icon
- **Target**: The `i` element (icon) inside the note listitem

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `note_item.locator("i")` | Direct icon selector | Works reliably |
| `note_item.locator(".note-menu-icon")` | Class-based | May not exist |

**CHOSEN**: `locator("i")` inside the note listitem - Targets the icon element directly

**VERIFIED PLAYWRIGHT CODE**:
```python
note_content = context.get("edited_note_content")
note_item = inner_iframe.get_by_role("listitem").filter(has_text="EDITED:")
# Click the three dots menu icon
note_item.locator("i").click()
page.wait_for_timeout(500)
```

- **Wait for**: Menu appears with View/Edit, Clone, Remove options

---

## Step 4: Click Remove Option

- **Action**: Click
- **Target**: "Remove" menu item

**VERIFIED PLAYWRIGHT CODE**:
```python
remove_option = inner_iframe.get_by_role("listitem").filter(has_text="Remove")
remove_option.click()
page.wait_for_timeout(500)
```

- **Wait for**: Confirmation dialog appears

---

## Step 5: Confirm Deletion

- **Action**: Click
- **Target**: "Ok" button in confirmation dialog

**LOCATOR DECISION:**

| Option | Pros | Cons |
|--------|------|------|
| `get_by_role("button", name="Ok")` | Semantic | In outer iframe |
| `locator("button").filter(has_text="Ok")` | Works | Less specific |

**CHOSEN**: `get_by_role("button", name="Ok")` - Clean semantic selector

**VERIFIED PLAYWRIGHT CODE**:
```python
ok_button = outer_iframe.get_by_role("button", name="Ok")
ok_button.click()
page.wait_for_timeout(1000)
```

- **Wait for**: Dialog closes, note removed from list

---

## Step 6: Verify Note Deleted

- **Action**: Verify
- **Target**: Note no longer appears in list

**VERIFIED PLAYWRIGHT CODE**:
```python
# Verify the note is no longer visible
deleted_note = inner_iframe.get_by_role("listitem").filter(has_text="EDITED:")
expect(deleted_note).not_to_be_visible(timeout=5000)
```

---

## Context Cleanup

```python
# Clean up note-related context
if "created_note_content" in context:
    del context["created_note_content"]
if "edited_note_content" in context:
    del context["edited_note_content"]
if "created_note_timestamp" in context:
    del context["created_note_timestamp"]
```
