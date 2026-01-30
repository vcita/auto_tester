# Events Teardown - Changelog

## 2026-01-27 - Healed (Error page after delete_client navigation - root cause: not on dashboard)
**Phase**: test.py, script.md
**Author**: Cursor AI (heal)
**Reason**: Services/Create Service fails after Events teardown because browser is left on error page
**Error**: Services/Create Service: `ValueError: Could not find Settings link. Current URL: https://www.vcita.com/app/dashboard. Page may be in unexpected state.`

**Root Cause**:
At timestamp 2:11 in test run video, during Events/_teardown Step 1 (delete client), the `fn_delete_client` function navigates to matter list by clicking `.menu-items-group > div:nth-child(4)`. This navigation leads to an error page ("This page is unavailable"). 

**The root cause**: After cancel_event, browser is on `/app/event-list`. Teardown Step 0 tries to navigate to dashboard but may fail silently. When `fn_delete_client` is called, it clicks `.menu-items-group > div:nth-child(4)` from event-list (or after failed dashboard navigation), which leads to error page instead of `/app/clients`. The 4th child selector may not be the matter list when on event-list page, or navigation from event-list to clients is broken.

**Fix Applied**:
1. **Enhanced Step 0**: Ensure we're on dashboard BEFORE calling delete_client. Added scroll_into_view, settle time, and wait_until="domcontentloaded" for reliable navigation. Added fallback via Settings if Dashboard fails.
2. After each delete operation (client and service), check if page is on error page by detecting "This page is unavailable" text
3. If error page detected, navigate away using "Return to homepage" link (if present) or direct navigation to dashboard
4. Final check before teardown completes to ensure we're not on error page
5. Use `page.goto()` for error recovery (allowed exception to navigation rules for error page recovery)

**Changes**:
- test.py Step 0: Enhanced dashboard navigation with scroll_into_view, settle time, wait_until="domcontentloaded", and Settings fallback
- test.py Step 1: Added error page detection and recovery after `fn_delete_client`
- test.py Step 2: Added error page detection and recovery after `fn_delete_service`
- test.py: Added final error page check before teardown completes
- script.md: Added Step 0 documentation with root cause explanation

**Verified Approach**: Based on video observation showing error page at 2:11. The error occurs when clicking `.menu-items-group > div:nth-child(4)` from event-list page. Ensuring we're on dashboard first prevents this.

**Note**: This may indicate a product bug where navigation to matter list from event-list page leads to error page. The test fix handles this by ensuring we're on dashboard first, but the root cause in the product should be investigated.

**Result**: ✅ Teardown should now leave browser on valid page (dashboard) instead of error page

---

## 2026-01-27 - Healed (Error page after delete_client navigation)
**Phase**: test.py
**Author**: Cursor AI (heal)
**Reason**: Services/Create Service fails after Events teardown because browser is left on error page
**Error**: Services/Create Service: `ValueError: Could not find Settings link. Current URL: https://www.vcita.com/app/dashboard. Page may be in unexpected state.`

**Root Cause**:
At timestamp 2:11 in test run video, during Events/_teardown Step 1 (delete client), the `fn_delete_client` function navigates to matter list by clicking `.menu-items-group > div:nth-child(4)`. This navigation leads to an error page ("This page is unavailable"). The teardown completes but leaves the browser on this error page, so Services/Create Service cannot find Settings/Dashboard links because they don't exist on the error page.

**Fix Applied**:
1. After each delete operation (client and service), check if page is on error page by detecting "This page is unavailable" text
2. If error page detected, navigate away using "Return to homepage" link (if present) or direct navigation to dashboard
3. Final check before teardown completes to ensure we're not on error page
4. Use `page.goto()` for error recovery (allowed exception to navigation rules for error page recovery)

**Changes**:
- test.py Step 1: Added error page detection and recovery after `fn_delete_client`
- test.py Step 2: Added error page detection and recovery after `fn_delete_service`
- test.py: Added final error page check before teardown completes

**Verified Approach**: Based on video observation showing error page at 2:11. Error page has distinctive "This page is unavailable" text and "Return to homepage" link.

**Note**: This may indicate a product bug where navigation to matter list after certain operations leads to error page. The test fix handles this, but the root cause in the product should be investigated.

**Result**: ✅ Teardown should now leave browser on valid page (dashboard) instead of error page
