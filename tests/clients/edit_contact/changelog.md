# Edit Contact Test - Changelog

## 2026-01-26 - Healed (Datepicker blocking Referred by click)
- **Error**: `TimeoutError: Locator.click: Timeout 30000ms exceeded` waiting for "Referred by" textbox click.
- **Why it passed before**: The test was built (2026-01-21) and run with the previous account (e.g. itzik+autotest@vcita.com from env/setup default). After switching to **create_user** and running with the **new user** (itzik+autotest.<timestamp>@vcita.com, Home Services / Landscaper), the Edit contact dialog for that vertical has a **Birthday** field whose position in the form’s **tab order** is right after Address. So the same test code (Tab after Address to “dismiss autocomplete”) now focused Birthday and opened the datepicker, which then blocked the Referred by click. So the regression was caused by **account/vertical change**, not a product change.
- **Root cause** (from heal request + MCP): After editing Address, test used Tab to dismiss autocomplete. Tab moved focus to Birthday (date field), which opened the MD datepicker overlay; that overlay intercepted pointer events so the click on "Referred by" never reached the field. (Later attempts: Escape or scroll_into_view still failed—element detached or not visible.)
- **Fix (protocol, no arbitrary waits)**: Do not use Tab. Click the dialog title "Edit contact info" to dismiss address autocomplete and avoid focusing Birthday; then click "Referred by" and fill. No `wait_for_timeout`.
- **Files updated**: test.py, script.md.
- **Validated**: Clients category re-run; Edit Contact passed (13.8s).

## 2026-01-21 - Initial Build
**Phase**: All files (steps.md, script.md, test.py, changelog.md)
**Author**: Cursor AI (exploration with Playwright MCP)
**Reason**: Built new test to edit contact information fields

**Changes**:
- Created steps.md defining test objective and flow
- Explored edit contact dialog using Playwright MCP browser
- Created script.md with LOCATOR DECISION tables and VERIFIED PLAYWRIGHT CODE
- Generated test.py from script.md
- Added edit_contact to _category.yaml between edit_matter and delete_matter

**Key Findings During Exploration**:
- Edit contact button is located at: `.contact-header > .v-icon.notranslate.edit-button`
- Dialog opens in outer_iframe (angularjs), not inner_iframe (vue_iframe_layout)
- All contact fields use standard textbox role with name labels
- To clear fields, use click + Ctrl+A + press_sequentially pattern
- Address field has Google Places autocomplete - clicking next field dismisses dropdown
- Save button is in dialog footer: `get_by_role("button", name="Save")`

**Fields Edited**:
1. Last Name - textbox "Last Name"
2. Address - textbox "Address" 
3. Referred by - textbox "Referred by"

**Context Operations**:
- Reads: created_matter_id, created_matter_name
- Writes: edited_last_name, edited_address, edited_referred_by, created_matter_name (updated)
