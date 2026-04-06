# Edit Matter - Detailed Script

> **Status**: Verified with Playwright MCP
> **Last Updated**: 2026-04-05
> **Note**: "Matter" is vcita's general entity - "Property" for Home Services, "Client" for generic, etc.

## Prerequisites
- Must run after `create_matter` test
- Requires context: `created_matter_id`, `created_matter_name`

## Initial State
- URL: Matter detail page `/app/clients/{matter_id}` (from create_matter)
- User is logged in (via category setup)

## Actions

### Step 1-2: Verify on matter page
- Check URL contains matter_id
- Wait for page title to contain matter_name

### Step 3: Open edit dialog
- Wait for `iframe[title="angularjs"]`
- Get nested iframe: `outer_iframe > #vue_iframe_layout`
- Find matter name button in inner iframe, then click edit button (`.nth(2)`)

### Step 4: Wait for edit dialog (entity-agnostic)
- **HEALED 2026-04-05**: Try each entity name: "Edit client info", "Edit property info", etc.
- Falls back to regex match: `text=/Edit .+ info/i`

### Step 5: Edit fields (adaptive)
**Property vertical** (has "How can we help you?" field):
- Edit "How can we help you?" textbox
- Edit "Special instructions/requests" textbox

**Client vertical** (has "Add tags" only):
- Add a tag via the tags input field
- Press Enter to confirm the tag

### Step 6: Save
- Click Save/SAVE button
- Wait for dialog to close

### Step 7: Verify (adaptive)
**Property**: Reopen dialog, verify field values match edited data
**Client**: Reopen dialog, verify tag text is visible

## Iframe Handling Notes
- Outer iframe: `iframe[title="angularjs"]` — contains edit dialog
- Inner iframe: `#vue_iframe_layout` inside outer — contains matter card and edit button
- Edit button is in inner iframe, dialog appears in outer iframe

## Context Updates
- `edited_tag`: (Client) tag that was added
- `edited_help_request`: (Property) new help request value
- `edited_special_instructions`: (Property) new instructions value
