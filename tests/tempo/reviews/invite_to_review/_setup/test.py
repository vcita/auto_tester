"""Setup for the reviews invite_to_review subcategory.

Mirrors the legacy reviews.feature scenario-1 preconditions: enable the reviews
feature flags, log in to the isolated account, and create a client via API
(capturing the client-portal JWT token used to open the portal as that client).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, enable_features

CLIENT_FIRST_NAME = "first"
CLIENT_LAST_NAME = "last"

# The POV reviews settings page redirects to the dashboard unless reviews_rollout
# and collect_reviews are on, and its fields stay disabled without
# enable_reviews_auto_publishing. The legacy env had these globally; enable them
# explicitly on the isolated account for determinism.
REVIEW_FEATURES = ",".join(
    [
        "reviews_rollout",
        "collect_reviews",
        "enable_reviews_auto_publishing",
    ]
)


def setup_reviews_invite(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Enable reviews feature flags (before login)")
    enable_features(context, REVIEW_FEATURES)

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Create client via API (capturing portal token)")
    email = f"reviewer+{int(time.time() * 1000)}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, email)
    context["review_client"] = client
    context["created_client_name"] = client["full_name"]

    print(f"  [OK] reviews setup complete - client '{client['full_name']}' ready")
