# Create Appointment Test - Changelog

## 2026-01-23 - Initial Build

**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration with Playwright MCP

**Changes**:
- Created steps.md defining appointment creation flow
- Generated script.md from MCP exploration with verified locators
- Generated test.py from script.md

**Verified Locators**:
- New button: `inner_iframe.get_by_role('button', name='New')`
- Appointment menu item: `inner_iframe.get_by_role('menuitem', name='Appointment')`
- Client search: `outer_iframe.get_by_role('textbox', name='Search by name, email or tag')`
- Client in list: `outer_iframe.get_by_role('button').filter(has_text=client_name)`
- Service search: `inner_iframe.get_by_role('searchbox', name='Search')`
- Select button: `inner_iframe.get_by_role('button', name='Select', exact=True)`
- Schedule button: `inner_iframe.get_by_role('button', name='Schedule appointment')`
- Success message: `page.get_by_text("Appointment scheduled")`
- Appointment in calendar: `inner_iframe.get_by_role('menuitem').filter(has_text=client_name)`

**Notes**:
- Calendar uses nested iframes: outer (angularjs) and inner (#vue_iframe_layout)
- Client selection dialog appears in outer iframe
- Service selection and scheduling in inner iframe
- Success toast appears in main page (outside iframes)
- Appointment appears as menuitem in calendar grid
