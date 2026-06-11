from playwright.sync_api import Page

from tests.account_api import deny_features, enable_features
from tests.spotlights.dashboard.app_widgets_manager.app_widgets_helpers import (
    assert_widget_count,
    is_widget_shown,
    open_dashboard,
)


def test_widget_filter(page: Page, context: dict) -> None:
    """The sales widget is gated by the payments_module feature flag.

    Migrates automation-js `app-widgets-manager.feature` scenario `widget filter`.
    """
    print("  Step 1: Denying payments_module, reloading dashboard...")
    deny_features(context, "payments_module")
    open_dashboard(page)
    assert_widget_count(page, 5)
    assert not is_widget_shown(page, "sales"), "Sales widget should be hidden when payments_module is denied"

    print("  Step 2: Re-enabling payments_module, reloading dashboard...")
    enable_features(context, "payments_module")
    open_dashboard(page)
    assert is_widget_shown(page, "sales"), "Sales widget should be shown when payments_module is enabled"
    print("  [OK] Sales widget follows the payments_module feature flag")
