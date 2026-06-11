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
else `className`, else tag name. Per-page hover/conditional icons are dropped via
the legacy `excludeIconForPageUtil` list (dashboard `edit-button`, inbox
`side_pane_true/false`, calendar `service-item-menu-activator`).

## Layer pass condition (per layer)
Poll the layer and pass once `total > 0`, the `total` is **stable across two
consecutive polls**, and `hidden` is empty. The count-stability gate prevents
asserting mid-render while icons are still appearing. If the count never settles
but `hidden` is empty by the deadline, it still passes.

## Intentional deviation from legacy
Every layer in `pageIframeLayers` is expected to render icons, so `total == 0`
after the poll window is treated as a **failure** ("page/layer failed to load"),
not a pass. Legacy `allHiddenIcons.should.be.empty` passes vacuously when no
icons are found; the migration tightens this to avoid a false positive when a
page or iframe layer never loads. No assertion or scope was dropped.

## Wait policy (bounded exceptions to the 5s element cap)
All are justified by the 3-level POV → Angular → Vue iframe boot plus lazy
icon-font rendering; none are fixed sleeps gating assertions:
- `goto` `domcontentloaded`: 30s (`NAV_TIMEOUT`) — cross-iframe page load.
- Angular iframe attach: 20s (`FRAME_TIMEOUT`).
- Per-layer poll window: 30s (`LAYER_POLL_SECONDS`) at a 0.5s interval, to absorb
  lazy icon rendering.
- One 1s post-nav settle (`SETTLE_MS`) before scanning, then condition polling.
