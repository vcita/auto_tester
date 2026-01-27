# Create User - Discovery (Playwright MCP)

## Signup entry

- **Login page**: base_url + "/login" (from config `target.base_url`; e.g. `https://www.vcita.com/login`).
- **Signup link**: At the **bottom** of the login page: text "Don't have an account?" followed by link **"Sign Up"** (url `/signup`). Same page shows either login form or signup form.

## Signup form (after clicking Sign Up)

- **URL**: Stays on `https://www.vcita.com/login?sso=true`; the view switches to Sign Up.
- **Heading**: "Sign Up" (level=1).
- **Fields**:
  - **Email**: label "Email", textbox (placeholder " ").
  - **Your Name or Business Name**: textbox with label/placeholder "Your Name or Business Name".
  - **Password**: label "Password", textbox.
- **Submit**: button **"Let's go"**.
- **Footer**: "Already have an account?" with link "Login" (`/login`).

### Playwright selectors (from snapshot)

- Sign Up link on login page: `page.get_by_role("link", name="Sign Up")` or `page.locator('a[href="/signup"]')`.
- Email: `page.get_by_label("Email")` or first textbox in signup form.
- Name: `page.get_by_label("Your Name or Business Name")` or `page.get_by_placeholder("Your Name or Business Name")`.
- Password: second textbox in form or `page.get_by_label("Password", exact=False)` (there may be two Password labels; use the one in the signup section).
- Submit: `page.get_by_role("button", name="Let's go")`.

### Assumptions

- Email verification: If vcita sends a verification email, automated run may require a pre-verified address or a test harness that reads the inbox. Document here if confirmed.
- Default password for new test users: **vcita123** (per plan).

## First-login flow (onboarding dialogs)

**Important**: Dialogs appear **inside the angular iframe**, not in the top-level page. Use the same frame for all dialog detection and dismissal when on `app.vcita.com`.

### Frame and checklist detection (refined via MCP)

- **Frame**: App iframe is **injected after load** (~5s). On **app.vcita.com** it has `id="angular-iframe"` and `title="angularjs"`. On **www.vcita.com** the same app may load with the iframe having different attributes initially. Use a **resilient selector** so the wait and dismissal work on both hosts: `iframe#angular-iframe, iframe[title="angularjs"], iframe[src*="child_app=true"]`. Use the same "on app" check everywhere: `/app/` in URL and `vcita` in URL (not only `app.vcita.com`), so frame-based logic runs on www too.
- **Checklist / "Let's personalize"**: The first-time checklist is a **dialog inside this iframe**. Reliable detection:
  - Dialog content contains "Let's personalize your account!" or "Congratulations! You're done!", or
  - The close button is visible: `frame.locator('#auto-checklist-close-btn').is_visible()`.
- **Close checklist**: `frame.locator('#auto-checklist-close-btn').click(timeout=10000)`. The × has id `#auto-checklist-close-btn`; it is not among the `[role="dialog"] button` list (that list is "Get app", "Add team").
- **Page overlay**: While the checklist is open, the wrapper on the main page has class `angular-iframe isModalMode` (and `isFullscreen`), so the iframe covers the viewport and the top-bar avatar is not clickable. After closing the dialog, the wrapper may keep `isModalMode`; use **logout URL fallback** when UI logout fails.

### Dialog 1: Welcome to vcita

- **Title/copy**: "Welcome to vcita!" / "Just a few basic questions to set you up right"
- **Location**: Inside angular iframe. Use `frame = page.frame_locator('iframe[title="angularjs"]')` or `page.frame_locator('#angular-iframe')`. Dialog: `frame.locator('[role="dialog"], .md-dialog').first()`.
- **Required fields**:
  - **Country code** – listbox `frame.get_by_role('listbox', name=re.compile(r'Country code:'))`. Open and choose e.g. "United States (1)", "United Kingdom (44)", "Israel (972)". Default is Israel (972).
  - **Phone** – `frame.get_by_role('textbox', name='Phone *')`. Server-validated via `validate_phone` API; invalid/unknown numbers return **422** and show "Invalid phone number". Empty shows "This field cannot be empty". Use a number that vcita accepts (param `phone` or env `VCITA_TEST_PHONE`).
  - **Business size** – listbox `frame.get_by_role('listbox', name=re.compile(r'Business size:'))`. Open and select **"I do not have a business"** (or "1 Person", etc.).
- **Optional**: Website URL (`frame.get_by_role('textbox', name='Website URL')`), **Your business address** – `frame.get_by_role('textbox', name='Your business address')` or `frame.locator('input[name="address"]')` (filled by create_user with param/VCITA_TEST_ADDRESS or "123 Test Street"). Field uses **Google Places autocomplete**; after fill, a dropdown appears – dismiss it with **Escape** before clicking Continue so the dropdown doesn’t block the button. Checkbox "Present my phone number & address to my clients".
- **Google Places dropdown**: After filling the address field, one **Escape** key closes the dropdown, keeps the typed text, and leaves Continue clickable (MCP-validated).
- **Dismiss**: No Skip/Later. Fill required fields and click **Continue**: `frame.get_by_role('button', name='Continue')`.
- **Order**: 1) Business size → "I do not have a business", 2) Country code (if changing), 3) Phone number, 4) Address (optional; create_user fills it), 5) Continue.
- **Phone format**: For Israel (972), use **national format with leading 0** (e.g. `0526111116`). Server rejects many test numbers (e.g. US 555, UK 77009); use param `phone` or env `VCITA_TEST_PHONE` with a number vcita accepts.

### Dialog 2: What does your business do?

- **Title/copy**: "What does your business do?" / "We'll streamline your setup experience accordingly"
- **Location**: Same dialog (wizard step) in angular iframe.
- **Controls**: Combobox "Search by profession or industry"; example chips: Accountant, Landscaper, Law firm, Construction company, Massage therapist, Tax Services, Yoga studio, Online Learning, Marketing agency, Beauty salon.
- **Dismiss**: Click one profession button (e.g. `frame.get_by_role('button', name='Accountant')`), then `frame.get_by_role('button', name='Continue')`.
- **Back** button returns to Dialog 1.

### Dialog 3: What are your business needs?

- **Title/copy**: "What are your business needs?"
- **Options** (clickable cards): Managing clients, Billing & payments, Online scheduling, Email & SMS marketing, Documents & forms, Secure portal for clients.
- **Dismiss**: Click one option (e.g. `frame.get_by_text('Managing clients', exact=False).first` or the containing generic), then Continue.

### Dialog 4: What do your clients pay for?

- **Title/copy**: "What do your clients pay for?" / "This will allow us to show you features that will help your services and products. Select all that apply."
- **Options**: Individual sessions, Multiple sessions, Programs & Projects, Bundled services & products, Physical products, Periodical fee / subscription, Other.
- **Dismiss**: Click one option (e.g. "Individual sessions"), then Continue.

### Dialog 5: You're ready for takeoff!

- **Title/copy**: "You're ready for takeoff!" / "Sit tight, we'll take you through your setup."
- **Dismiss**: Click `frame.get_by_role('button', name='GO')`.

### Dialog 6: Let's personalize your account! (checklist, 3 steps)

- **Title/copy**: "Let's personalize your account!" with progress "1/3 completed" … "3/3 completed" / "Congratulations! You're done!"
- **Step 1/3**: "Add your clients & contacts" — **Skip** (`frame.get_by_role('button', name='Skip')`).
- **Step 2/3**: "Add website widgets" — **Skip**; then "Edit client portal" — **Skip** (two Skip buttons in sequence).
- **Step 3/3**: "Get the mobile app" / "Invite team members" — no Skip; close the dialog via **close button**: `frame.locator('#auto-checklist-close-btn').click()` (or the × at top).
- **Result**: Dialog closes; dashboard with no onboarding overlay.

## Validation (no dialog on second login)

- After dismissing all onboarding dialogs, **log out** (use `fn_logout`: user avatar → Logout).
- **Log in again** with the same credentials.
- **Assert**: For at least 10 seconds, no modal/dialog appears (e.g. no `[role="dialog"]`, no overlay with "Skip" / "Get started"). If a dialog appears, the account is not yet "ready"; retry dismissal or fail.

## Logout (reference)

- User menu: button with user initials (e.g. "AU") or "AU Autotest" → menu opens.
- Click menu item with text **"Logout"** (class `logout-item` in DOM).
- Wait for redirect to `**/login**`.
