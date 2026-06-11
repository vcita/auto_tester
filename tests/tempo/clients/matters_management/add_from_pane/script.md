# Add Matter From Contact Pane - Script

> Status: Verified live on integration 2026-06-08 (VCITA2-13952)

## Initial State
- Logged in; `contact_client_id` / `contact_client_email` in context.

## Frames
- Matter page: `iframe[title="angularjs"]` (outer) → `#vue_iframe_layout` (inner).

## Actions (`matters_helpers.add_matter_from_pane`)
1. Open contact matter page: `page.goto(base + /app/clients/{contact_id})`,
   wait for inner `.matter-name-title` (bounded open: 1 + 2 retries, each wait ≤5s).
2. Inner `.add-matter-button` → native click (`el.click()`); the control intercepts a
   normal Playwright click (Angular-Material), so dispatch a native click like the
   legacy `clickWebElementByJS`.
3. Outer md-dialog "Add Client" → click `[ng-click='continue()']` (CONTINUE).
4. Outer matter-name field `f-client-field[field*='matterName'] input` → fill `matter_1`.
5. Outer `button:has-text('Save')` → click. Wait for dialog (`[ng-click='continue()']`) hidden.

## Verification (`assert_matter_under_contact`)
- Re-open the contact matter page; assert inner `.matter-list-row` texts contain `matter_1`
  (bounded re-check 1 + 2) and inner `.tooltips-wrapper .info-row_text-value` == contact email.

## Selector notes
- No `data-qa` exists on the contact-pane add button or the matter-name field; suggested
  data-qa to add in product: `data-qa="add-matter-button"`, `data-qa="matter-name-input"`.
