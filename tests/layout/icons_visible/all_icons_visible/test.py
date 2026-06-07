"""Migrates automation-js `features/spotlights/icons.feature`.

Verifies that design-system icons render (none present-but-hidden) across the
frontage iframe layers on the main pages: dashboard, inbox, calendar, CRM.
"""

import time

from playwright.sync_api import Page, Frame

from tests._functions._config import get_base_url

ANGULAR_IFRAME = 'iframe[title="angularjs"]'

# Icon selectors per iframe layer (mirror the legacy Layout page object).
POV_ICONS = (
    '[data-qa="VcIcon"]:not([data-exclude-icon-test] [data-qa="VcIcon"], '
    '.draggable-tabs [data-qa="VcIcon"])'
)
VUE_ICONS = '[data-qa="VcIcon"]:not([data-exclude-icon-test] [data-qa="VcIcon"])'
ANGULAR_ICONS = "md-icon:not(f-help-center md-icon)"

# page -> (relative path, ordered layers) — from legacy pageIframeLayers.
PAGES = {
    "dashboard": ("/app/dashboard", ["pov"]),
    "inbox": ("/app/inbox", ["pov", "angular"]),
    "calendar": ("/app/calendar", ["pov", "vue"]),
    "CRM": ("/app/clients", ["pov"]),
}

LAYER_SELECTOR = {"pov": POV_ICONS, "angular": ANGULAR_ICONS, "vue": VUE_ICONS}

# Known hover/conditional icons that are legitimately hidden by default — mirrors
# the legacy `excludeIconForPageUtil` in steps/desktop/layout.js.
PAGE_EXCLUDE_ICONS = {
    "dashboard": ["edit-button"],
    "inbox": ["side_pane_true", "side_pane_false"],
    "calendar": ["service-item-menu-activator"],
    "CRM": [],
}

NAV_TIMEOUT = 30_000
FRAME_TIMEOUT = 20_000
LAYER_POLL_SECONDS = 30
SETTLE_MS = 1_000
POLL_INTERVAL_MS = 500

# Returns {total, hidden:[identifier,...]} for `selector` within a frame.
# "hidden" mirrors Selenium isDisplayed: no client rects / visibility:hidden / display:none.
_HIDDEN_ICONS_JS = """
(selector) => {
  const els = Array.from(document.querySelectorAll(selector));
  const hidden = [];
  for (const el of els) {
    const style = window.getComputedStyle(el);
    const visible = el.getClientRects().length > 0
      && style.visibility !== 'hidden'
      && style.display !== 'none';
    if (!visible) {
      const tagged = el.parentElement && el.parentElement.closest('[data-qa]');
      const id = (tagged && tagged.getAttribute('data-qa'))
        || (el.parentElement && el.parentElement.getAttribute('data-qa'))
        || el.className
        || el.tagName.toLowerCase();
      hidden.push(String(id));
    }
  }
  return { total: els.length, hidden };
}
"""


def _app_base(page: Page, context: dict) -> str:
    if "/app/" in page.url:
        return page.url.split("/app/")[0]
    return get_base_url(context).rstrip("/")


def _angular_frame(page: Page) -> Frame:
    handle = page.wait_for_selector(ANGULAR_IFRAME, state="attached", timeout=FRAME_TIMEOUT)
    frame = handle.content_frame()
    if frame is None:
        raise AssertionError("angularjs iframe present but has no content frame")
    return frame


def _descendant_frames(frame: Frame) -> list:
    """All frames nested under `frame` (the Vue layer lives inside the Angular frame)."""
    collected = []
    for child in frame.child_frames:
        collected.append(child)
        collected.extend(_descendant_frames(child))
    return collected


def _layer_frames(page: Page, layer: str) -> list:
    if layer == "pov":
        return [page.main_frame]
    angular = _angular_frame(page)
    if layer == "angular":
        return [angular]
    if layer == "vue":
        return _descendant_frames(angular)
    raise ValueError(f"unknown layer: {layer}")


def _scan_layer(page: Page, layer: str, excludes: list) -> dict:
    """Aggregate {total, hidden} across all frames that make up `layer`,
    dropping known hover/conditional icons (legacy excludeIconForPageUtil)."""
    selector = LAYER_SELECTOR[layer]
    total = 0
    hidden: list = []
    for frame in _layer_frames(page, layer):
        try:
            result = frame.evaluate(_HIDDEN_ICONS_JS, selector)
        except Exception:
            continue  # frame detached/navigated mid-scan; re-checked on next poll
        total += result["total"]
        hidden.extend(h for h in result["hidden"] if h not in excludes)
    return {"total": total, "hidden": hidden}


def _assert_layer_icons_visible(page: Page, page_name: str, layer: str, excludes: list) -> None:
    """Wait for the layer's icons to render and their count to settle, then assert
    none are hidden.

    Every layer in the legacy `pageIframeLayers` mapping is expected to render
    icons, so `total == 0` after the timeout means the page/layer never loaded and
    is a failure (not a vacuous pass). The count must be stable across two polls so
    we don't assert mid-render while icons are still appearing.
    """
    deadline = time.monotonic() + LAYER_POLL_SECONDS
    prev_total = -1
    last = {"total": 0, "hidden": []}
    while time.monotonic() < deadline:
        last = _scan_layer(page, layer, excludes)
        if last["total"] > 0 and last["total"] == prev_total and not last["hidden"]:
            print(f"     [OK] {page_name}/{layer}: {last['total']} icons, none hidden")
            return
        prev_total = last["total"]
        time.sleep(POLL_INTERVAL_MS / 1000)

    if last["total"] == 0:
        raise AssertionError(
            f"{page_name} page, {layer} layer: no icons found within "
            f"{LAYER_POLL_SECONDS}s (page/layer failed to load)"
        )
    if not last["hidden"]:
        print(f"     [OK] {page_name}/{layer}: {last['total']} icons, none hidden (no steady count)")
        return
    raise AssertionError(
        f"{page_name} page, {layer} layer: hidden icons "
        f"({len(last['hidden'])}/{last['total']}): {sorted(set(last['hidden']))}"
    )


def _check_page(page: Page, context: dict, page_name: str) -> None:
    rel_path, layers = PAGES[page_name]
    excludes = PAGE_EXCLUDE_ICONS.get(page_name, [])
    print(f"  Navigating to {page_name} page ({rel_path})...")
    page.goto(f"{_app_base(page, context)}{rel_path}", wait_until="domcontentloaded", timeout=NAV_TIMEOUT)

    if "angular" in layers or "vue" in layers:
        _angular_frame(page)  # ensure the angular iframe attached before scanning
    page.wait_for_timeout(SETTLE_MS)

    for layer in layers:
        _assert_layer_icons_visible(page, page_name, layer, excludes)


def test_all_icons_visible(page: Page, context: dict) -> None:
    """No design-system icon is present-but-hidden on dashboard/inbox/calendar/CRM."""
    for page_name in ("dashboard", "inbox", "calendar", "CRM"):
        _check_page(page, context, page_name)
    print("  [OK] All icons visible across dashboard, inbox, calendar, and CRM")
