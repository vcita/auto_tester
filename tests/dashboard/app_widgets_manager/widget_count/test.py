from playwright.sync_api import Page

from tests.dashboard.app_widgets_manager.app_widgets_helpers import (
    assert_widget_count,
    open_dashboard,
)


def test_widget_count(page: Page, context: dict) -> None:
    """With new_dashboard enabled, the dashboard shows the 6 default widgets.

    Migrates automation-js `app-widgets-manager.feature` scenario
    `New dashboard loading`.
    """
    print("  Opening dashboard, expecting 6 widgets...")
    open_dashboard(page)
    assert_widget_count(page, 6)
    print("  [OK] Dashboard shows 6 widgets")
