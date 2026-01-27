# Create Client Function - Changelog

## 2026-01-26 - Healed (Navigate to dashboard via UI)

**Phase**: test.py
**Author**: Cursor AI (heal_test)
**Reason**: Appointments/_setup failed after create_service: timeout waiting for get_by_text("Quick actions", exact=True). create_client used page.goto(base_url + "/app/dashboard"), which can load a wrong or empty page (e.g. base_url is www; app is on app.vcita.com).

**Fix Applied**: Navigate to dashboard via UI: if not already on /app/dashboard, click sidebar "Dashboard" and wait for URL; then wait for Quick actions. Aligns with create_matter and avoids page.goto to internal URLs.

**Changes**: test.py Step 1 only.

---

## 2026-01-23 - Initial Build

**Phase**: All files
**Author**: Cursor AI
**Reason**: Created function for test setup - adapted from tests/clients/create_matter/test.py

**Changes**:
- Created steps.md defining minimal client creation flow
- Created script.md documenting verified code from create_matter test
- Created test.py with simplified client creation logic

**Verified Locators** (inherited from create_matter test):
- Quick actions text: `page.get_by_text("Quick actions", exact=True)`
- Add property: `page.get_by_text("Add property", exact=True)`
- First Name field: `form_frame.get_by_role("textbox", name="First Name *")`
- Last Name field: `form_frame.get_by_role("textbox", name="Last Name")`
- Email field: `form_frame.get_by_role("textbox", name="Email")` / `form_frame.get_by_role("combobox", name="Email")`
- Save button: `form_frame.get_by_role("button", name="Save")`

**Notes**:
- Minimal client creation - only fills required fields plus name and email
- Email field transforms to combobox when clicked (autocomplete behavior)
- Client ID extracted from URL pattern `/app/clients/([^/]+)`
- "Matter" = "Property" in Home Services vertical
