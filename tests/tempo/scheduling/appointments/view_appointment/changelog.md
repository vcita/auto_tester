# View Appointment Test - Changelog

## 2026-01-23 - Initial Build

**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration with Playwright MCP

**Changes**:
- Created steps.md defining appointment viewing flow
- Generated script.md from MCP exploration with verified locators
- Generated test.py from script.md

**Verified Locators**:
- Calendar appointment: `inner_iframe.get_by_role('menuitem').filter(has_text=client_name)`
- Appointment heading: `outer_iframe.get_by_role('heading', name='Appointment')`
- Client name: `outer_iframe.get_by_text(client_name)`
- Service name: `outer_iframe.get_by_role('heading', name=service_name)`
- Date/time: `outer_iframe.get_by_role('heading', level=2)`
- Back button: `page.get_by_text('Back')`

**Notes**:
- Clicking appointment navigates to `/app/appointments/{id}` page
- Details appear in outer iframe (angularjs frame)
- Service name appears as h3 heading
- Date/time appears as h2 heading
- Back button returns to calendar
