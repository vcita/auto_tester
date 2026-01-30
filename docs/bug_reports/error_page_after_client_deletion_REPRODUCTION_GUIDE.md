# Minimal Reproduction Guide: Error Page After Client Deletion

## Quick Steps (5 minutes)

### Prerequisites
- Logged into vcita: `itzik+autotest.1769462440@vcita.com` / `vcita123`
- At least one client/property exists

### Steps

1. **Go to Dashboard**
   - Navigate to: `https://www.vcita.com/app/dashboard`
   - Or click "Dashboard" in sidebar

2. **Open Clients/Properties List**
   - Click the 4th menu item in the sidebar (Properties/Clients/Patients)
   - Should navigate to: `/app/clients`

3. **Find a Client**
   - Search for an existing client name in the search box
   - Click on the client row to open detail page
   - Should navigate to: `/app/clients/{client_id}`

4. **Delete the Client**
   - Click "More" dropdown button (in iframe)
   - Click "Delete property" (or "Delete client")
   - Click "Ok" in confirmation dialog

5. **BUG OCCURS HERE** ⚠️
   - **Expected**: Redirects to `/app/clients` (matter list)
   - **Actual**: Redirects to error page "This page is unavailable"

### What You Should See

**Error Page Shows:**
```
This page is unavailable

Please verify that the URL is valid and that you have permissions to view the page.

[Return to homepage] (link)
```

**Visual Confirmation:**
- Red 'X' icon
- Bold text: "This page is unavailable."
- Blue underlined link: "Return to homepage"
- vcita logo in top-left corner

**Instead of:**
- Matter list page (`/app/clients`)
- Client no longer in the list

---

## Alternative: Using Test Flow

If you want to reproduce using the exact test flow that triggers the bug:

1. **Run Events subcategory tests** (creates a client for event)
2. **Cancel an event** (leaves browser on `/app/event-list`)
3. **Navigate to dashboard** (via sidebar)
4. **Delete the event client** (follow steps 2-4 above)
5. **Bug should appear** after deletion confirmation

---

## Notes

- **Reproduction Rate**: Intermittent (not 100% reliable)
- **More likely to occur**: After Events subcategory operations
- **Workaround**: Click "Return to homepage" link on error page

## Automated Reproduction Attempt

**Status**: ⚠️ **Partially Verified**

**What Was Verified:**
- ✅ Error page appearance confirmed (screenshot captured)
- ✅ Error page text matches: "This page is unavailable"
- ✅ "Return to homepage" link exists and is clickable
- ❌ Full reproduction blocked by CAPTCHA during login

**CAPTCHA Limitation:**
Automated browser testing cannot bypass CAPTCHA challenges. Manual reproduction is required for full verification.

**Screenshot**: Error page screenshot captured showing exact UI elements and text.
