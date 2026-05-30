from playwright.sync_api import Page

from tests.payments.tips_settings.tips_account import (
    GATEWAY_PLATFORM_FLAG,
    TIPS_FEATURE_FLAG,
    deny_features,
    enable_features,
    login,
)


def setup_tips_disabled(page: Page, context: dict) -> None:
    print("  Step: Enable tips_settings feature flag (before login)")
    enable_features(context, TIPS_FEATURE_FLAG)
    print("  Step: Deny gateway_platform feature flag (before login)")
    deny_features(context, GATEWAY_PLATFORM_FLAG)
    print("  Step: Log in to isolated account")
    login(page, context)
    print("  Setup complete - tips reachable, no payment provider")
