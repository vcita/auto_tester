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

## Output Expectations

When asked to author tests, produce selectors that:

- Start with `data-qa` when available.
- Use one consistent fallback strategy if `data-qa` is missing.
- Stay readable and easy to maintain.
