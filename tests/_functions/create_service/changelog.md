# Create Service Function - Changelog

## 2026-01-23 - Initial Build

**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration with Playwright MCP

**Changes**:
- Created steps.md defining minimal service creation flow
- Generated script.md from MCP exploration with verified locators
- Generated test.py from script.md

**Verified Locators**:
- Settings navigation: `page.get_by_text('Settings')`
- Services button: `iframe.get_by_role('button', name='Define the services your')`
- New service dropdown: `iframe.get_by_role('button', name='New service icon-caret-down')`
- 1 on 1 menu item: `iframe.get_by_role('menuitem', name='on 1 appointment')`
- Service name field: `iframe.get_by_role('textbox', name='Service name *')`
- Face to face button: `iframe.get_by_role('button', name='icon-Home Face to face')`
- No fee button: `iframe.get_by_role('button', name='No fee')`
- Create button: `iframe.get_by_role('button', name='Create')`

**Notes**:
- Includes workaround for service list not auto-refreshing after creation
- Service ID extracted from URL pattern `/services/([a-z0-9]+)`
- Creates free service with Face to Face location and default 1 hour duration
