---
name: prefer-data-qa-selectors
description: Prioritizes stable element selection for UI test authoring by using data-qa selectors first, then semantic fallbacks when needed. Use when creating or updating Playwright tests, adding new UI interactions, or when the user asks to improve selector reliability.
---

# Prefer data-qa Selectors

## Instructions

When building or updating UI tests:

1. Prefer `data-qa` selectors as the first option for element targeting.
2. If a `data-qa` selector is unavailable, use semantic selectors (`get_by_role`, labeled fields) before text/CSS fallback.
3. Keep selector intent explicit and consistent across the file.
4. If a stable selector is missing, note that `data-qa` should be added in the app code.

## UI Scope Preservation

Do not replace a UI action with an API call when that action is part of the behavior the test, reusable function, or helper is meant to cover.

- Stabilize the selector, wait, navigation, or product readiness signal instead of bypassing the UI.
- API setup is acceptable for prerequisites that are outside the tested behavior.
- API cleanup is acceptable only when cleanup itself is not the tested behavior and does not replace a reusable UI action function whose objective is to exercise the UI.
- If replacing UI with API is proposed, explicitly confirm that the removed UI path is outside scope before making the change.

## Selector Priority

Use this order:

1. `page.locator('[data-qa="..."]')`
2. `page.get_by_role(...)` with accessible name
3. `page.get_by_label(...)` / `page.get_by_placeholder(...)`
4. `page.get_by_text(...)` (only when stable and unique)
5. Raw CSS/XPath as last resort

## Playwright Examples

Preferred:

```python
save_button = page.locator('[data-qa="invoice-save-button"]')
save_button.click()
```

Balanced fallback:

```python
save_button = page.locator('[data-qa="invoice-save-button"]')
if save_button.count() == 0:
    save_button = page.get_by_role("button", name="Save")
save_button.click()
```

Avoid brittle selectors:

```python
# Avoid when a stable data-qa is available:
page.locator("div > div:nth-child(3) > button").click()
```

## Reduce Waits And Duration (Without Scope Or Quality Loss)

Selector choices should help tests run faster without weakening reliability:

- Stable `data-qa` selectors let you wait on a precise readiness signal instead of fixed sleeps; pair the selector with an explicit condition wait, not an arbitrary delay.
- Do not weaken a selector or drop an in-scope UI action to shave time; stabilize the selector or wait instead.
- Reduce duration by removing redundant navigation/reloads and avoidable UI setup, never by removing assertions or in-scope UI steps.

## Output Expectations

When asked to author tests, produce selectors that:

- Start with `data-qa` when available.
- Use one consistent fallback strategy if `data-qa` is missing.
- Stay readable and easy to maintain.
