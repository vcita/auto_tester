# All Icons Visible — Script (HOW)

## Page → iframe-layer mapping (from legacy `pageIframeLayers`)
| page      | path            | layers          |
|-----------|-----------------|-----------------|
| dashboard | /app/dashboard  | POV             |
| inbox     | /app/inbox      | POV, Angular    |
| calendar  | /app/calendar   | POV, Vue        |
| CRM       | /app/clients    | POV             |

## Frame acquisition (Playwright)
- POV layer → `page.main_frame`.
- Angular layer → content frame of `iframe[title="angularjs"]`.
- Vue layer → the Vue iframe nested inside the Angular frame (scan all descendant
  frames of the Angular frame so we don't depend on a single iframe id).

## Hidden-icon detection (per frame)
Run one `frame.evaluate(...)` that does `querySelectorAll(selector)` and returns
`{total, hidden}`, where an element is *hidden* when it has no client rects, or
`visibility:hidden`, or `display:none` (matches Selenium `isDisplayed`). The
identifier mirrors legacy: nearest `[data-qa]` ancestor, else parent `data-qa`,
else `className`.

## Stability
- After `goto`, wait for `domcontentloaded` and (for Angular/Vue pages) for the
  Angular iframe to attach.
- Poll each layer up to a timeout: pass as soon as `hidden` is empty; this absorbs
  lazy icon-font rendering. A layer with zero matching icons passes (matches the
  legacy assertion, which only fails on present-but-hidden icons).
- Only fixed waits replaced by condition polling; no scope/assertion removed.
