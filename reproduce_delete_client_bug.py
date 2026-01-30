"""
Script to reproduce the bug where deleting a client redirects to an error page
instead of redirecting to /app/clients.

This script follows the exact steps from tests/_functions/delete_client/test.py
to reproduce the product bug.
"""

import re
import time
from playwright.sync_api import sync_playwright

# Configuration from config.yaml
BASE_URL = "https://www.vcita.com"
USERNAME = "itzik+autotest.1769462440@vcita.com"
PASSWORD = "vcita123"

# Test client name - you can modify this to use an existing client
# or the script will create one first
CLIENT_NAME = None  # Will be set if creating a client


def login(page):
    """Log in to vcita"""
    print("Step: Logging in...")
    login_url = f"{BASE_URL}/login"
    page.goto(login_url, wait_until="commit")
    page.wait_for_load_state("domcontentloaded")
    
    # Handle Cloudflare if present
    if "Just a moment" in page.title() or page.title() == "":
        print("  [!] Cloudflare security check detected - waiting...")
        try:
            page.wait_for_function(
                """() => {
                    const title = document.title || '';
                    return !title.includes('Just a moment') && title !== '' && title.length > 0;
                }""",
                timeout=120000
            )
            print("  [OK] Cloudflare check passed!")
        except Exception as e:
            print(f"  [X] Cloudflare timeout")
            raise e
    
    # Wait for login form
    email_field = page.get_by_label("Email", exact=True)
    email_field.wait_for(state="visible", timeout=60000)
    
    # Fill login form
    email_field.click()
    page.wait_for_timeout(100)
    email_field.fill(USERNAME)
    
    password_field = page.get_by_label("Password", exact=True)
    password_field.click()
    page.wait_for_timeout(100)
    password_field.fill(PASSWORD)
    
    # Click login button (note: it's "Login" not "Log in")
    login_btn = page.get_by_role("button", name="Login")
    login_btn.click()
    
    # Wait for dashboard (handle CAPTCHA if needed)
    try:
        page.wait_for_url("**/app/dashboard**", timeout=120000)
    except Exception as e:
        current_url = page.url
        if "captcha" in current_url.lower():
            print("  [!] reCAPTCHA detected - please solve it manually...")
            page.wait_for_url("**/app/dashboard**", timeout=120000)
        else:
            raise e
    
    page.wait_for_load_state("domcontentloaded")
    print("  [OK] Logged in successfully")


def create_test_client(page):
    """Create a test client to delete"""
    global CLIENT_NAME
    timestamp = int(time.time())
    first_name = "Test"
    last_name = f"DeleteBug{timestamp}"
    CLIENT_NAME = f"{first_name} {last_name}"
    email = f"test_delete_{timestamp}@vcita-test.com"
    
    print(f"\nStep: Creating test client '{CLIENT_NAME}'...")
    
    # Navigate to dashboard if not already there
    if "/app/dashboard" not in page.url:
        dashboard_link = page.get_by_text("Dashboard", exact=True)
        dashboard_link.wait_for(state="visible", timeout=15000)
        dashboard_link.click()
        page.wait_for_url("**/app/dashboard**", timeout=15000)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)
    
    # Wait for Quick Actions Panel
    page.get_by_text("Quick actions", exact=True).wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(3000)
    
    # Click Add matter (using regex pattern from test code)
    quick_section = page.get_by_text("Quick actions", exact=True).locator("../..")
    add_matter_text = quick_section.get_by_text(re.compile(r"^Add (property|client|patient|matter)", re.IGNORECASE))
    add_matter_text.wait_for(state="visible", timeout=15000)
    add_matter_text.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    add_matter_text.click()
    
    # Find form frame
    form_frame = None
    max_attempts = 10
    for attempt in range(max_attempts):
        page.wait_for_timeout(500)
        for frame in page.frames:
            try:
                if frame.locator('text=First Name').count() > 0:
                    form_frame = frame
                    break
            except:
                pass
        if form_frame:
            break
        print(f"    Attempt {attempt + 1}/{max_attempts}: Form not found yet...")
    
    if not form_frame:
        raise Exception("Could not find form frame with 'First Name' field")
    
    form_frame.locator('text=First Name').wait_for(timeout=15000)
    
    # Fill form
    first_name_field = form_frame.get_by_role("textbox", name="First Name *")
    first_name_field.click()
    first_name_field.press_sequentially(first_name, delay=50)
    
    last_name_field = form_frame.get_by_role("textbox", name="Last Name")
    last_name_field.click()
    last_name_field.press_sequentially(last_name, delay=50)
    
    email_field = form_frame.get_by_role("textbox", name="Email")
    email_field.click()
    page.wait_for_timeout(100)
    form_frame.get_by_role("combobox", name="Email").press_sequentially(email, delay=30)
    
    # Save
    save_btn = form_frame.get_by_role("button", name="Save")
    save_btn.click()
    page.wait_for_url(re.compile(r"/app/clients/"), timeout=30000)
    
    print(f"  [OK] Created client: {CLIENT_NAME}")
    return CLIENT_NAME


def delete_client(page, client_name):
    """Delete a client and check for the error page bug"""
    print(f"\n{'='*60}")
    print(f"REPRODUCING BUG: Deleting client '{client_name}'")
    print(f"{'='*60}\n")
    
    # Step 1: Navigate to matter list
    print("Step 1: Navigating to matter list...")
    if not (BASE_URL in page.url and "/app/" in page.url):
        page.goto(f"{BASE_URL}/app/dashboard")
        page.wait_for_load_state("domcontentloaded")
    
    matter_list_nav = page.locator(".menu-items-group > div:nth-child(4)")
    matter_list_nav.wait_for(state="visible", timeout=10000)
    matter_list_nav.click()
    page.wait_for_url("**/app/clients", timeout=10000)
    page.wait_for_timeout(1000)
    print("  [OK] Navigated to clients list")
    
    # Step 2: Search for Client
    print(f"Step 2: Searching for client: {client_name}")
    search_field = page.get_by_role('searchbox', name='Search by name, email, or phone number')
    search_field.click()
    page.wait_for_timeout(100)
    search_field.press_sequentially(client_name, delay=30)
    page.wait_for_timeout(1000)
    print("  [OK] Searched for client")
    
    # Step 3: Click on Client in List
    print("Step 3: Opening client detail page...")
    client_row = page.get_by_role('row').filter(has_text=client_name)
    client_row.wait_for(state='visible', timeout=5000)
    client_row.click()
    page.wait_for_url("**/app/clients/**", timeout=10000)
    print("  [OK] Opened client detail page")
    
    # Step 4: Click More Dropdown
    print("Step 4: Opening More menu...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    more_btn = iframe.get_by_role('button', name='More icon-caret-down')
    more_btn.wait_for(state='visible', timeout=10000)
    more_btn.click()
    menu = iframe.get_by_role('menu')
    menu.wait_for(state='visible', timeout=5000)
    print("  [OK] Opened More menu")
    
    # Step 5: Select Delete
    print("Step 5: Clicking Delete...")
    delete_option = iframe.get_by_role("menuitem").filter(has_text=re.compile(r"^Delete ", re.IGNORECASE))
    delete_option.first.click()
    dialog = iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=5000)
    print("  [OK] Delete dialog opened")
    
    # Step 6: Confirm Deletion
    print("Step 6: Confirming deletion...")
    ok_btn = iframe.get_by_role('button', name='Ok')
    ok_btn.click()
    print("  [OK] Clicked Ok - waiting for redirect...")
    
    # Wait for dialog to close
    dialog.wait_for(state='hidden', timeout=10000)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)  # Give it time to redirect
    
    # Check for error page
    print("\n" + "="*60)
    print("CHECKING FOR BUG...")
    print("="*60)
    
    current_url = page.url
    page_text = page.locator("body").text_content() or ""
    
    print(f"\nCurrent URL: {current_url}")
    
    # Check if we're on an error page
    if "This page is unavailable" in page_text or "page is unavailable" in page_text.lower():
        print("\n" + "!"*60)
        print("[BUG] BUG REPRODUCED! Error page detected after deletion!")
        print("!"*60)
        print("\nError page text found in body:")
        print("-" * 60)
        
        # Try to get more details about the error page
        error_elements = page.locator("text=/This page is unavailable/i")
        if error_elements.count() > 0:
            print("Found error message element")
        
        homepage_link = page.get_by_text("Return to homepage", exact=False)
        if homepage_link.count() > 0:
            print("Found 'Return to homepage' link")
        
        # Take a screenshot
        screenshot_path = "bug_reproduction_error_page.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\nScreenshot saved to: {screenshot_path}")
        
        print("\nExpected behavior: Should redirect to /app/clients")
        print(f"Actual behavior: Redirected to error page at {current_url}")
        
        return True  # Bug reproduced
    else:
        # Check if we're on the clients list (expected behavior)
        if "/app/clients" in current_url and "/app/clients/" not in current_url:
            print("\n  [OK] No bug - correctly redirected to /app/clients")
            return False
        else:
            print(f"\n  [WARNING] Unexpected state - URL is: {current_url}")
            print("Not on error page, but also not on /app/clients")
            return None


def main():
    """Main reproduction flow"""
    print("="*60)
    print("Bug Reproduction: Error Page After Client Deletion")
    print("="*60)
    print("\nThis script will:")
    print("1. Log in to vcita")
    print("2. Create a test client (or use existing one)")
    print("3. Delete the client")
    print("4. Check if error page appears (BUG)")
    print("\n" + "="*60 + "\n")
    
    with sync_playwright() as p:
        # Launch browser (headless=False so you can see what's happening)
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            # Login
            login(page)
            
            # Create a test client (or you can modify CLIENT_NAME to use existing)
            if CLIENT_NAME is None:
                client_name = create_test_client(page)
            else:
                client_name = CLIENT_NAME
            
            # Wait a bit before deletion
            print("\nWaiting 2 seconds before deletion...")
            page.wait_for_timeout(2000)
            
            # Delete and check for bug
            bug_reproduced = delete_client(page, client_name)
            
            print("\n" + "="*60)
            if bug_reproduced:
                print("RESULT: [SUCCESS] BUG SUCCESSFULLY REPRODUCED")
                print("The error page appeared after client deletion.")
            elif bug_reproduced is False:
                print("RESULT: [NO BUG] Bug not reproduced this time")
                print("The deletion worked correctly (redirected to /app/clients)")
            else:
                print("RESULT: [WARNING] Unexpected state")
            print("="*60)
            
            # Keep browser open for inspection
            print("\nBrowser will stay open for 30 seconds for inspection...")
            print("Press Ctrl+C to close immediately")
            page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"\n[ERROR] Error occurred: {e}")
            import traceback
            traceback.print_exc()
            # Keep browser open on error
            print("\nBrowser will stay open for inspection...")
            page.wait_for_timeout(30000)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
