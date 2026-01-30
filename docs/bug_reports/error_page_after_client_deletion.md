# Bug Report: Error Page After Client Deletion

## Summary
After successfully deleting a client (matter/property), the product sometimes redirects to an error page ("This page is unavailable") instead of redirecting to the matter list (`/app/clients`) as expected.

## Severity
**Medium** - Affects user experience and test automation reliability

## Environment
- **Product**: vcita
- **Account**: Home Services vertical (uses "Properties" terminology)
- **Reproduction Rate**: Intermittent (appears more frequently after Events subcategory operations)

## Steps to Reproduce

### Prerequisites
1. Logged into vcita account: `itzik+autotest.1769462440@vcita.com`
2. Have at least one client/property created
3. (Optional but increases likelihood) Have recently completed Events subcategory operations (schedule event, cancel event)

### Reproduction Steps

1. **Navigate to Dashboard**
   - Ensure you're on `/app/dashboard`
   - If not, click "Dashboard" in the sidebar

2. **Navigate to Matter List (Properties/Clients)**
   - Click the 4th item in the sidebar menu (`.menu-items-group > div:nth-child(4)`)
   - This should navigate to `/app/clients`
   - Wait for the page to fully load

3. **Search for a Client**
   - In the search box (labeled "Search by name, email, or phone number"), type the name of an existing client
   - Wait for search results to appear

4. **Open Client Detail Page**
   - Click on the client row in the search results
   - This should navigate to `/app/clients/{client_id}`
   - Wait for the client detail page to load (iframe with `title="angularjs"` should be visible)

5. **Open More Menu**
   - In the iframe, find and click the "More" dropdown button (labeled "More icon-caret-down")
   - Wait for the dropdown menu to appear

6. **Select Delete Option**
   - Click the menu item that starts with "Delete" (e.g., "Delete property", "Delete client", "Delete patient")
   - Wait for the confirmation dialog to appear

7. **Confirm Deletion**
   - Click the "Ok" button in the confirmation dialog
   - **BUG OCCURS HERE**: After the dialog closes, instead of redirecting to `/app/clients`, the page redirects to an error page

### Expected Behavior
After clicking "Ok" to confirm deletion:
- The confirmation dialog should close
- The page should automatically redirect to `/app/clients` (matter list)
- The deleted client should no longer appear in the list

### Actual Behavior
After clicking "Ok" to confirm deletion:
- The confirmation dialog closes
- The page redirects to an error page showing:
  - Message: "This page is unavailable"
  - A "Return to homepage" link
- The user is stuck on the error page and must manually navigate away

## Error Page Details

**Error Message**: "This page is unavailable"

**Error Page Elements**:
- Heading: "This page is unavailable"
- Link: "Return to homepage" (navigates to `/app/dashboard`)

**URL Pattern**: The error page URL may vary, but typically shows an error state

## Technical Details

### Code Location
The bug occurs in the automatic redirect logic after client deletion. The product code should:
1. Delete the client from the database
2. Close the confirmation dialog
3. Redirect to `/app/clients` (matter list)

Instead, step 3 redirects to an error page.

### Test Code Reference
- Function: `tests/_functions/delete_client/test.py`
- Step 6: After `ok_btn.click()`, the product should redirect but sometimes shows error page
- Detection: Check for "This page is unavailable" text in page body

### Workaround
The test suite now detects this error page and automatically navigates to dashboard:
```python
page_text = page.locator("body").text_content() or ""
if "This page is unavailable" in page_text or "page is unavailable" in page_text.lower():
    # Navigate away from error page
    homepage_link = page.get_by_text("Return to homepage", exact=False)
    if homepage_link.count() > 0:
        homepage_link.click()
```

## Additional Context

### When Bug Occurs More Frequently
- After completing Events subcategory operations (schedule event, cancel event)
- When deleting clients that were created during Events subcategory tests
- When navigating from `/app/event-list` to matter list

### Related Issues
- This bug may be related to navigation state management after certain operations
- The error page appears during the automatic redirect, not during manual navigation

## Screenshots/Logs

**Error Page Screenshot**: Captured during automated reproduction attempt
- Shows: "This page is unavailable" message
- Shows: "Return to homepage" link
- Shows: Red 'X' error icon
- Shows: vcita logo in header

**Note**: Full automated reproduction was blocked by CAPTCHA during login. Manual reproduction is required to verify the complete flow.

## Suggested Fix
1. Investigate the redirect logic after client deletion
2. Ensure proper navigation state management
3. Add error handling for failed redirects
4. Consider adding a fallback navigation to dashboard if redirect fails

## Test Automation Impact
- Test suite now includes error page detection and recovery
- This adds complexity to test code but ensures tests can continue
- The root cause should be fixed in the product to prevent this issue

---

**Reported By**: Test Automation (discovered during test execution)  
**Date**: 2026-01-27  
**Status**: Open - Needs Product Team Investigation
