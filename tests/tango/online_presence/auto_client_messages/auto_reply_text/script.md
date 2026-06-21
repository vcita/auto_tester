# Auto Reply Text Change — Detailed Script

Migrated from `automation-js/features/tango/auto-client-messages.feature`.
All selectors below were **verified live on integration via Playwright MCP**
(app.meet2know.com settings + live.meet2know.com livesite). Implementation lives in
`tests/tango/online_presence/auto_client_messages/auto_client_messages_helpers.py`.

Legacy ground truth: `node index features/tango/auto-client-messages.feature
--env integration --headless` → 1 scenario / 4 steps passed (~45s, directory recurly).

## Initial State
- Logged in to the isolated account (from `_setup`).

## Actions

### Step 1: Update the auto-reply message in settings
- **Action**: Call helper `update_auto_reply(page, context, "bla2")`
- **Target**: Settings "Messages & Documents" tab + TinyMCE auto-reply editor + Save.

**KEY FRAME TOPOLOGY (verified):** the entire legacy settings page renders inside
`#angular-iframe`. The TinyMCE auto-reply editor is nested one level deeper:
`#angular-iframe` -> `.mce-edit-area iframe` -> `#tinymce`. The save-confirmation
toast renders at the TOP page level (outside the angular iframe).

**LOCATOR DECISION (tab):**

| Option | Pros | Cons |
|--------|------|------|
| `frame_locator("#angular-iframe").get_by_role("tab", name=...)` | semantic | Playwright found 0 `role=tab` here (Angular md-tabs not exposed) |
| `span[translate="settings.client_notifications.tabs.messages"][aria-hidden="false"]` | stable Angular translate key; aria-hidden filters the hidden dummy tab | translate-key based |

**CHOSEN**: `span[translate="settings.client_notifications.tabs.messages"][aria-hidden="false"]`
inside `#angular-iframe` — verified: clicking it selects the Messages & Documents tab.

**LOCATOR DECISION (editor):** `.mce-edit-area iframe` -> `#tinymce` (legacy
`message_iframe` / `iframeBody`); TinyMCE-stable, no `data-qa`. Contenteditable →
focus then `keyboard.type` (project rule); clear first with Select-All + Delete
(legacy `_enterTextToNonInputElement` clears before typing).

**LOCATOR DECISION (save):** `button[data-qa="action-button-client_notifications-save"]`
— exact legacy `data-qa`. Verified: the button does NOT disable after save, so the
real signal is the toast (below), not button state.

**VERIFIED PLAYWRIGHT CODE** (see helper `update_auto_reply`):
```python
page.goto(f"{base}/app/settings/messages", wait_until="domcontentloaded")
settings = page.frame_locator("#angular-iframe")
save = settings.locator('button[data-qa="action-button-client_notifications-save"]').first
save.wait_for(state="visible", timeout=20000)
tab = settings.locator('span[translate="settings.client_notifications.tabs.messages"][aria-hidden="false"]').first
tab.wait_for(state="visible", timeout=5000); tab.click()
body = settings.frame_locator(".mce-edit-area iframe").locator("#tinymce")
body.wait_for(state="visible", timeout=20000); body.click()
body.press("Control+a"); body.press("Delete")
body.press_sequentially("bla2", delay=40)        # per-char keyup feeds the editor
expect(body).to_have_text("bla2", timeout=5000)
page.wait_for_timeout(1500)                       # debounced TinyMCE->Angular ng-model sync
save.click()
page.get_by_text("Changes saved").first.wait_for(state="visible", timeout=5000)
```
- **CRITICAL (verified via network capture):** the auto-reply maps to the
  `messages_auto_response` settings field, saved via `PUT /v2/settings`. The
  TinyMCE -> Angular ng-model binding is **debounced on input**: the PUT body only
  carries `messages_auto_response` once the debounce fires after the last
  keystroke. A bulk `type()` and/or saving immediately drops the field (PUT then
  sends only unrelated nulled keys) and the livesite keeps the default reply.
  `press_sequentially` (per-char keyup) + a minimal bounded 1.5s debounce wait
  flush the value — confirmed: PUT body then contains
  `messages_auto_response: "<div>bla2</div>"` and the livesite shows "bla2".
- **How verified**: live on a runner-like (automation-flagged) account — saved
  "bla2", PUT carried `messages_auto_response`, then the livesite success page
  read back "bla2".
- **Wait for / outcome**: top-level "Changes saved" alert (legacy success toast).

### Step 2: Leave details on the public livesite
- **Action**: Call helper `leave_details_on_livesite(page, context, details)`
- **Target**: livesite `<CP_VITRAGE>/site/<pivot_uid>` → "Leave details" action →
  contact form inside `#cp_iframe`.

**LOCATOR DECISION (livesite base):** reuse `estimates_helpers.CP_VITRAGE`
(`https://live.meet2know.com`, == legacy integration `vitrage`) + `pivot_uid(context)`.
Public visitor URL (no client_jwt) — the leave-details flow is a public action.

**LOCATOR DECISION (action):** `a.business-action[ng-href*="leave-details"]` (legacy,
verified: 1 visible match; `#cp_iframe` appears after the click).

**LOCATOR DECISION (form fields):** legacy used `//label[text()='X']/../input`, but the
current Vuetify form does NOT nest input under label (those XPaths returned 0).
Verified working: `#cp_iframe` `get_by_label("<Label>", exact=True)` for
Subject / Message / Email / First Name / Last Name (count 1 each). Each filled only
if a value is present (legacy fills conditionally). Submit:
`get_by_role("button", name="Submit")`.

**VERIFIED PLAYWRIGHT CODE** (see helper `leave_details_on_livesite`):
```python
page.goto(f"{CP_VITRAGE}/site/{pivot_uid(context)}", wait_until="domcontentloaded")
page.locator('a.business-action[ng-href*="leave-details"]').first.click()
cp = page.frame_locator("#cp_iframe")
cp.get_by_label("Subject", exact=True).first.wait_for(state="visible", timeout=20000)
cp.get_by_label("Subject", exact=True).first.fill("hi")        # + Message/Email/First Name/Last Name
cp.get_by_role("button", name="Submit").first.click()
```
- **Details (legacy data table)**:
  `{"subject":"hi","message":"hello","email":"form+<seq>@vmeetme.com",
    "first_name":"form_first","last_name":"form_last"}` (`<seq>` unique per run).
- **How verified**: filled all five labels live and submitted; success page rendered.

### Step 3: Verify the success page shows the auto-reply text (OUTCOME)
- **Action**: Call helper `assert_success_message(page, "bla2")`
- **Target**: `#cp_iframe` `div.second-row` (legacy `successMessage`).

**CHOSEN**: `frame_locator("#cp_iframe").locator("div.second-row")` — exact legacy
selector, verified live. Assert **equal** to the configured auto-reply text
(legacy `.eql`).

**VERIFIED PLAYWRIGHT CODE** (see helper `assert_success_message`):
```python
cp = page.frame_locator("#cp_iframe")
success = cp.locator("div.second-row").first
success.wait_for(state="visible", timeout=20000)
expect(success).to_have_text("bla2", timeout=5000)
```
- **How verified**: after submitting the leave-details form, `div.second-row` read
  back exactly **"bla2"** — the value saved in Step 1 (full end-to-end proof).

## Success Verification (state-change outcome)
- The livesite success page displays exactly the auto-reply text configured in
  Step 1 — end-to-end proof the settings update persisted and is served publicly.

## Wait policy
- Element/interaction waits: `UI_TIMEOUT = 5000`.
- `NAV_TIMEOUT = 20000` only at the settings (#angular-iframe), TinyMCE editor,
  livesite, and `#cp_iframe` (re)load points, always tied to a concrete readiness
  signal (save button visible, tab visible, TinyMCE body visible, leave-details link
  visible, Subject field visible, success row visible). No retries.
- One unavoidable fixed wait: `wait_for_timeout(1500)` after typing the auto-reply,
  for the debounced TinyMCE -> Angular ng-model sync. No external state exposes the
  debounce; the value is otherwise dropped from the save payload. Bounded under 2s
  and documented (the sole fixed wait in the flow).
