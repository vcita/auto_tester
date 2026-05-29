from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

UI_TIMEOUT = 5_000


def open_calendar_page(page: Page) -> None:
    if "/app/calendar" in page.url and _calendar_new_button_is_visible(page):
        return

    _goto_calendar_page(page)
    if _calendar_new_button_is_visible(page):
        return

    _reload_calendar_page(page)
    if _calendar_new_button_is_visible(page):
        return

    _open_calendar_via_menu(page)
    if _calendar_new_button_is_visible(page):
        return

    _goto_dashboard_page(page)
    _goto_calendar_page(page)
    _wait_for_calendar_new_button(page)


def _open_calendar_via_menu(page: Page) -> None:
    try:
        calendar_menu = page.get_by_text("Calendar", exact=True)
        calendar_menu.wait_for(state="visible", timeout=UI_TIMEOUT)
        calendar_menu.click(timeout=UI_TIMEOUT)

        calendar_view_item = page.get_by_text("Calendar View", exact=True)
        calendar_view_item.wait_for(state="visible", timeout=UI_TIMEOUT)
        calendar_view_item.evaluate("element => element.click()")
        page.wait_for_url("**/app/calendar**", timeout=UI_TIMEOUT)
    except PlaywrightTimeoutError:
        return


def _goto_calendar_page(page: Page) -> None:
    page.goto(f"{_app_base_url(page)}/app/calendar", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    page.wait_for_url("**/app/calendar**", timeout=UI_TIMEOUT)


def _goto_dashboard_page(page: Page) -> None:
    page.goto(f"{_app_base_url(page)}/app/dashboard", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    page.wait_for_url("**/app/dashboard**", timeout=UI_TIMEOUT)


def _reload_calendar_page(page: Page) -> None:
    page.reload(wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    page.wait_for_url("**/app/calendar**", timeout=UI_TIMEOUT)


def _wait_for_calendar_new_button(page: Page) -> None:
    page.wait_for_selector('iframe[title="angularjs"]', timeout=UI_TIMEOUT)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator("#vue_iframe_layout")
    inner_iframe.get_by_role("button", name="New").wait_for(
        state="visible",
        timeout=UI_TIMEOUT,
    )


def _calendar_new_button_is_visible(page: Page) -> bool:
    try:
        _wait_for_calendar_new_button(page)
        return True
    except PlaywrightTimeoutError:
        return False


def _app_base_url(page: Page) -> str:
    if "/app/" not in page.url:
        raise ValueError(f"Cannot infer app base URL from current page URL: {page.url}")
    return page.url.split("/app/")[0]
