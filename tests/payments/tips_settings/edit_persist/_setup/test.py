from playwright.sync_api import Page

from tests.payments.tips_settings.tips_account import (
    TIPS_FEATURE_FLAG,
    enable_features,
    login,
)
from tests.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_tips_edit_persist(page: Page, context: dict) -> None:
    print("  Step: Enable tips_settings feature flag (before login)")
    enable_features(context, TIPS_FEATURE_FLAG)
    print("  Step: Log in to isolated account")
    login(page, context)
    print("  Step: Connect mock payment gateway")
    connect_mock_gateway(page, context)
    print("  Setup complete - mock gateway connected, tips enabled")
