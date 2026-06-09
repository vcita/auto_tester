"""Setup for the staff_profile subcategory (isolated account).

Mirrors the legacy staff-profile-page.feature Background (denied
`pov_landing_page_routing`) and scenario 2's staff creation: deny the flag,
capture the owner staff (for the dynamic own-profile assertion), create a
second role=user staff, then log in. The profile edits/reads themselves are the
in-scope UI behavior and stay in the tests.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import deny_features
from tests.settings.staff_profile.staff_profile_api import create_user_staff, get_owner_staff


def setup_staff_profile(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Deny pov_landing_page_routing feature flag")
    deny_features(context, "pov_landing_page_routing")

    print("  Setup Step 2: Capture account owner staff")
    owner = get_owner_staff(context)

    seq = int(time.time())
    print("  Setup Step 3: Create second staff 'user_staff' (role user) via API")
    user_staff = create_user_staff(context, "user_staff", f"user+role+{seq}@vmeetme.com")

    print("  Setup Step 4: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    context.setdefault("staff_profile", {}).update(
        {"owner": owner, "user_staff": user_staff}
    )
    print(
        f"  [OK] setup complete - owner '{owner['display_name']}', "
        f"second staff '{user_staff['name']}' ({user_staff['email']})"
    )
