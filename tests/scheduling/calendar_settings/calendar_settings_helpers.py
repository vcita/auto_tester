from __future__ import annotations

from datetime import datetime

from playwright.sync_api import Error as PlaywrightError, Page, TimeoutError as PlaywrightTimeoutError, expect

from tests.scheduling.calendar.calendar_helpers import (
    get_calendar_frames,
    wait_for_calendar_idle,
    _close_settings_side_pane,
)

UI_TIMEOUT = 5_000
SIDE_NAV_SELECTOR = '[data-qa="calendar-settings-page__main-layout_page-side-nav"]'
SETTINGS_LOAD_ATTEMPTS = 3


def set_business_settings(page: Page, week_start_day: str, time_format: str) -> None:
    """Open the Calendar settings side pane and set Start-week + Time format.

    Mirrors legacy ``CalendarSettingsSidePane.setBusinessSettingsInSidePane``: open the
    scheduler settings dropdown -> Business settings, pick the two options, save through
    the side-pane save button, wait for it to disable (the save confirmation), and close.
    """
    _, vue = get_calendar_frames(page)
    wait_for_calendar_idle(vue)

    vue.locator('[data-qa="scheduler-settings-dropdown-activator"] [data-qa]').first.click(timeout=UI_TIMEOUT)
    vue.locator('[data-qa="option-open-business-settings"]').click(timeout=UI_TIMEOUT)

    start_week = vue.locator('[data-qa="business-settings-layout__main-body_start-week"]')
    start_week.wait_for(state="visible", timeout=UI_TIMEOUT)
    _choose_setting(vue, "business-settings-layout__main-body_start-week", week_start_day)
    _choose_setting(vue, "business-settings-layout__main-body_time-format", time_format)

    save = vue.locator('[data-qa="business-settings-layout_save-mobile"]').first
    save.wait_for(state="visible", timeout=UI_TIMEOUT)
    if save.is_enabled():
        save.click(timeout=UI_TIMEOUT)
        _wait_for_save_disabled(save)
    _close_settings_side_pane(page, vue)


def hide_weekends(page: Page) -> None:
    """Switch to Week view and toggle the weekend display off, mirroring legacy hideWeekEnds."""
    _, vue = get_calendar_frames(page)
    _ensure_week_view(vue)
    vue.locator('[data-qa="view-button"]').click(timeout=UI_TIMEOUT)
    vue.locator('[data-qa="option-toggle_show_weekend"]').click(timeout=UI_TIMEOUT)
    vue.locator("body").press("Escape")
    wait_for_calendar_idle(vue)


def get_calendar_week_display(page: Page) -> dict[str, str]:
    """Read the Week-view header: first weekday label, first hour label, weekday count.

    The legacy assertion had no save confirmation and relied on a fixed sleep; this polls
    the rendered header values until they are populated instead.
    """
    _, vue = get_calendar_frames(page)
    vue.locator('[smart-id="timelineHeaderHorizontalContent"]').first.wait_for(state="visible", timeout=UI_TIMEOUT)
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    last: dict[str, str] = {}
    while datetime.now().timestamp() < deadline:
        rows = vue.locator(".smart-scheduler-view-time")
        weekdays = rows.nth(0).locator(".timeline-header-weekday")
        hours = rows.nth(1).locator(".timeline-header-time")
        day_count = weekdays.count()
        if day_count > 0 and hours.count() > 0:
            last = {
                "week_start_day": weekdays.first.inner_text().strip(),
                "time_format": hours.first.inner_text().strip(),
                "num_of_days": str(day_count),
            }
            if last["week_start_day"] and last["time_format"]:
                return last
        vue.page.wait_for_timeout(150)
    raise AssertionError(f"Calendar week header did not render. Last read: {last}")


def open_calendar_settings_page(page: Page) -> None:
    page.goto(
        f"{_app_base_url(page)}/app/settings/calendar_settings",
        wait_until="domcontentloaded",
        timeout=UI_TIMEOUT,
    )
    page.wait_for_url("**/app/settings/calendar_settings**", timeout=UI_TIMEOUT)


def read_settings_side_nav(page: Page) -> dict[str, str]:
    """Read the Calendar Settings side-nav layout: staff-selector presence + tab count.

    Returns the same shape the legacy ``getSideNavLayout`` produced: string values for
    ``has_staff_select`` ("true"/"false") and ``settings_tabs`` (count).

    The settings sub-app can stay on its loading spinner (the side nav never mounts),
    especially right after an SSO staff switch, so resolving the side-nav frame is retried
    with a page reload, capped at SETTINGS_LOAD_ATTEMPTS.
    """
    vue = None
    for attempt in range(SETTINGS_LOAD_ATTEMPTS):
        try:
            vue = _settings_side_nav_frame(page)
            break
        except AssertionError:
            if attempt == SETTINGS_LOAD_ATTEMPTS - 1:
                raise
            page.reload(wait_until="domcontentloaded", timeout=UI_TIMEOUT)
            page.wait_for_url("**/app/settings/calendar_settings**", timeout=UI_TIMEOUT)
    side_nav = vue.locator(SIDE_NAV_SELECTOR)
    side_nav.wait_for(state="visible", timeout=UI_TIMEOUT)
    try:
        vue.locator('[data-qa="scheduler-page-loader"]').wait_for(state="hidden", timeout=UI_TIMEOUT)
    except PlaywrightTimeoutError:
        pass

    menu_items = side_nav.locator(".grouped-items__group__container__menu-item")
    menu_items.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    stable_count = menu_items.count()
    while datetime.now().timestamp() < deadline:
        vue.page.wait_for_timeout(150)
        current = menu_items.count()
        if current == stable_count:
            break
        stable_count = current

    has_staff_select = side_nav.locator(".staff-controller").count() == 1
    return {"has_staff_select": str(has_staff_select).lower(), "settings_tabs": str(stable_count)}


def _choose_setting(vue, block_qa: str, option_text: str) -> None:
    vue.locator(f'[data-qa="{block_qa}"] .settings-select__select-aria_select').click(timeout=UI_TIMEOUT)
    vue.get_by_text(option_text, exact=True).last.click(timeout=UI_TIMEOUT)


def _ensure_week_view(vue) -> None:
    scheduler = vue.locator("smart-scheduler.smart-element.smart-scheduler")
    if scheduler.get_attribute("view") == "week":
        return
    vue.locator('[data-qa="view-button"]').click(timeout=UI_TIMEOUT)
    vue.locator('[data-qa="option-week"]').click(timeout=UI_TIMEOUT)
    expect(scheduler).to_have_attribute("view", "week", timeout=UI_TIMEOUT)


def _wait_for_save_disabled(button) -> None:
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    while datetime.now().timestamp() < deadline:
        if not button.is_enabled():
            return
        button.page.wait_for_timeout(100)
    raise AssertionError("Business settings save did not disable after save")


def _settings_side_nav_frame(page: Page):
    """Return the frame that renders the Calendar Settings side nav.

    The settings page can render the Vuetage side nav in the top document, the Angular
    iframe, or a nested Vue iframe depending on the route's mount strategy, so resolve by
    finding whichever frame actually contains the side-nav element rather than guessing an
    iframe id.
    """
    deadline = datetime.now().timestamp() + (UI_TIMEOUT / 1000)
    while datetime.now().timestamp() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(SIDE_NAV_SELECTOR).count() > 0:
                    return frame
            except PlaywrightError:
                continue
        page.wait_for_timeout(200)
    frame_urls = [frame.url for frame in page.frames]
    raise AssertionError(f"Calendar settings side nav was not found in any frame. Frames: {frame_urls}")


def _app_base_url(page: Page) -> str:
    if "/app/" not in page.url:
        raise ValueError(f"Cannot infer app base URL from current page URL: {page.url}")
    return page.url.split("/app/")[0]
