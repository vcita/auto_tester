# Changelog — Auto Reply Text Change

## 2026-06-19 — Created (VCITA2-14249)
- Migrated `automation-js/features/tango/auto-client-messages.feature`
  (Scenario: "auto reply text change") into team `tango`, domain `online_presence`.
- Legacy ground truth confirmed live: `node index features/tango/auto-client-messages.feature
  --env integration --headless` → 1 scenario / 4 steps passed (~45s, directory recurly).
- Phase files authored in order: steps.md → script.md → test.py.
- Selectors taken from the legacy page objects
  (`Settings/autoClientMessages.js`, `Vitrage/livesite.js`):
  - Settings save: `button[data-qa="action-button-client_notifications-save"]` (data-qa).
  - TinyMCE auto-reply: `.mce-edit-area iframe` -> `#tinymce` (contenteditable; clear +
    `keyboard.type`).
  - Livesite leave-details action: `a.business-action[ng-href*="leave-details"]`.
  - Leave-details form fields by label XPath inside `#cp_iframe`; Submit
    `//button[contains(., 'Submit')]`.
  - Success page: `#cp_iframe` `div.second-row`, asserted EQUAL to the auto-reply text
    (legacy `.eql`).
- Reuse: `estimates_helpers.CP_VITRAGE` + `pivot_uid` for the livesite base + `#cp_iframe`
  pattern (same CP base used by coupons_checkout_cp.open_portal); `tests/_functions/login`.
- Outcome verification: assert the configured auto-reply text appears on the livesite
  success page (end-to-end proof the settings update persisted). Replaced the legacy
  success-toast wait on save with a save-button-disabled outcome wait (more reliable
  than a transient toast).
- Wait policy: element waits capped at 5s (UI_TIMEOUT); NAV_TIMEOUT=20000 only at
  settings/livesite/`#cp_iframe` (re)load points, tied to concrete readiness signals;
  no fixed sleeps, no retry loops.

## 2026-06-19 — Fixed selectors after live MCP verification (run 1 failed → corrected)
- First focused run failed (TimeoutError 20s) because the settings page renders the
  whole legacy Frontage UI inside `#angular-iframe`; the initial helper queried tabs /
  TinyMCE / save at the top page level. Confirmed live via Playwright MCP and corrected:
  - Settings frame topology: `#angular-iframe` -> tab
    `span[translate="settings.client_notifications.tabs.messages"][aria-hidden="false"]`;
    editor `#angular-iframe` -> `.mce-edit-area iframe` -> `#tinymce`.
  - Save confirmation: the save button does NOT disable after save; the real signal is
    the TOP-level "Changes saved" alert (`.v-alert.dialog-alert`, matched via
    `page.get_by_text("Changes saved")`). Replaced the (wrong) save-disabled wait.
  - Livesite leave-details form: legacy `//label[text()='X']/../input` XPaths return 0 on
    the current Vuetify form; switched to `#cp_iframe` `get_by_label("<Label>", exact=True)`
    for Subject/Message/Email/First Name/Last Name, Submit via
    `get_by_role("button", name="Submit")`.
  - End-to-end verified live: after saving "bla2" and submitting the leave-details form,
    `#cp_iframe` `div.second-row` read back exactly "bla2".

## 2026-06-19 — Fixed TinyMCE -> Angular sync (runner runs showed default reply)
- Runs 2-3 reached Step 3 but the livesite showed the DEFAULT reply ("Thank you for
  your message.") instead of "bla2". Network capture proved the cause: the auto-reply
  maps to the `messages_auto_response` settings field saved via `PUT /v2/settings`, and
  a bulk `type()`/`keyboard.type()` into the TinyMCE contenteditable updated the visible
  editor (and even `isDirty()`) but did NOT update the Angular ng-model, so the PUT body
  dropped `messages_auto_response` (it sent only unrelated nulled fields) and the save
  silently no-opped for the auto-reply.
- Fix (verified live on an automation-flagged, runner-like account):
  - Type with `press_sequentially(text, delay=40)` (per-char keyup feeds the editor)
    instead of bulk type — also aligns with the project text-input rule.
  - After typing, wait a minimal bounded 1.5s for the DEBOUNCED TinyMCE -> Angular
    ng-model sync before clicking save. Root cause confirmed via network capture: the
    binding is debounced on input; saving before it fires drops `messages_auto_response`
    from the PUT body. (A programmatic `focus()`/blur and an immediate save both still
    dropped the field; only the post-type debounce wait reliably flushes it.)
  - Confirmed the PUT then carries `messages_auto_response: "<div>bla2</div>"` and the
    livesite leave-details success page reads back exactly "bla2".
- Also confirmed there is NO directory dependency: legacy uses directory `recurly` ==
  integration directory 970, the same the runner uses. The earlier "default reply"
  symptom was the ng-model sync bug, not a directory/propagation issue.
- `Control+a`/`Delete` clear is done via `body.press(...)` (locator-scoped, keeps focus
  inside the nested TinyMCE frame); replaced the cross-frame `page.keyboard` clear.
