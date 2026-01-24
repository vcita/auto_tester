# Create Group Event - Changelog

## 2026-01-23 - Initial Build
**Phase**: All files
**Author**: Cursor AI (exploration with Playwright MCP)
**Reason**: Built from steps.md via browser exploration

**Changes**:
- Created steps.md with test objectives and steps
- Explored vcita application with Playwright MCP to discover:
  - Group event creation flow differs from 1-on-1 services
  - "New service" dropdown has "Group event" option
  - Group events have "Max attendees" field (unique to group events)
  - After creation, a dialog prompts to enter event dates/times
  - Group events display "X attendees" instead of "1 on 1" in list
- Generated script.md with verified Playwright code for each step
- Generated test.py from script.md
- Applied same UI bug workaround as create_service (refresh via navigation)

**Key Discoveries**:
- Menu item: `get_by_role("menuitem", name="Group event")`
- Max attendees: `get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")`
- Event times dialog: Must click "I'll do it later" to continue
- List indicator: "10 attendees" instead of "1 on 1"

**Context Variables Set**:
- `created_group_event_id`
- `created_group_event_name`
- `created_group_event_description`
- `created_group_event_duration` = 60
- `created_group_event_price` = 25
- `created_group_event_max_attendees` = 10
