# Create Appointment Test - Changelog

## 2026-01-31 - Healed (Address field not always visible)

**Phase**: test.py, script.md
**Author**: Cursor AI (heal_test)
**Reason**: TimeoutError waiting for Address textbox – "Timeout 10000ms exceeded" for `get_by_role("textbox", name=re "Address")`.

**Root Cause**: The New Appointment form does not always show the Address field (e.g. Location section may be collapsed or not in the current form layout). The test assumed Address was always present and waited 10s, causing failure when the form had no Address.

**Fix Applied**: Make Address fill optional. Form ready = Schedule button visible (single detection). Only fill Address if the textbox is already in the DOM (`address_field.count() > 0`); no wait for Address, so no timeout swallow (per Timeout Means Failure). If Address is present, fill and Tab to dismiss autocomplete; otherwise proceed to click Schedule.

**Changes**: test.py – replaced mandatory `address_field.wait_for(state='visible', timeout=10000)` with `if address_field.count() > 0:` block; script.md – Step 8b updated to optional fill with same code.

**Verified Approach**: Category re-run: Create Appointment and full appointments suite passed.

---

## 2026-01-26 - Healed (Google Places autocomplete intercepts Schedule click)

**Phase**: test.py, script.md
**Author**: Cursor AI (heal_test)
**Reason**: TimeoutError when clicking "Schedule appointment" – "pac-item from pac-container intercepts pointer events".

**Root Cause**: After filling the Address field, the Google Places autocomplete dropdown (pac-container/pac-item) stays visible and overlays the Schedule button, so the click is intercepted.

**Fix Applied**: After filling the Address field (Step 8b), press Escape to dismiss the autocomplete dropdown, then wait 400ms, before clicking Schedule appointment.

**Changes**: test.py – added `page.keyboard.press('Escape')` and short wait before Step 9; script.md – same in Step 8b VERIFIED PLAYWRIGHT CODE.

**Verified Approach**: Error call log identified pac-container as interceptor; Escape is standard way to dismiss address autocomplete.

---

## 2026-01-26 - Healed (Required Address field in New Appointment dialog)

**Phase**: test.py, script.md
**Author**: Cursor AI (heal_test)
**Reason**: Step 10 timed out waiting for appointment in calendar; screenshot showed "New Appointment" dialog still open with "Required field" on the Address under Location.

**Root Cause**: The dialog can require an Address when Location is "My business address". The test clicked "Schedule appointment" without filling it, so the form did not submit and the appointment was never created; the verification step then timed out looking for a menuitem with the client name.

**Fix Applied**: Before clicking Schedule, try to find and fill the Address field (by role textbox name matching "Address" or by placeholder). Fill with "123 Test Street". If the field is not present, continue (try/except). Added as Step 8b in script.md.

**Changes**: test.py – added `import re` and Address-fill block before Step 9; script.md – new Step 8b and VERIFIED PLAYWRIGHT CODE.

**Verified Approach**: Screenshot analysis; category re-run used for validation.

---

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
