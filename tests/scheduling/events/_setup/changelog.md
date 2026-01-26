# Events Setup Changelog

## 2026-01-25 - Product bug (test blocked)
**Phase**: N/A (no test change)
**Reason**: Create Group event step fails with API 422; dialog shows "Please fix the errors below". Confirmed via MCP: form is filled correctly but Create returns 422 and dialog never closes. Classified as **product/system bug** in vcita, not a test issue.

**Actions**:
- Bug report: `.cursor/bug_reports/group_event_create_422.md`
- Events _setup marked as `blocked` in `tests/scheduling/events/_category.yaml`
- No changes to test code.

## 2026-01-24 - Initial Build
**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration

**Changes**:
- Generated script.md from MCP exploration
- Generated test.py from script.md
- Creates group event service and test client for event scheduling tests
- Navigates to Calendar page after setup
