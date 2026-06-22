"""Setup for the roles_permissions subcategory (isolated account).

Mirrors the legacy roles-and-permissions.feature Background (login) and scenario
3's staff creation: create a role=User staff via the Platform API, then log in.
The role view/change behaviour itself is the in-scope UI behaviour and stays in
the tests.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_platform_staff_via_api


def setup_roles_permissions(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    seq = int(time.time())
    print("  Setup Step 1: Create staff 'user_staff' (role user) via API")
    user_staff = create_platform_staff_via_api(
        context, "user_staff", f"user+role+{seq}@vmeetme.com", role="user"
    )

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    context.setdefault("roles_permissions", {}).update({"user_staff": user_staff})
    print(
        f"  [OK] setup complete - staff '{user_staff['name']}' ({user_staff['email']}) "
        f"uid={user_staff['uid']}"
    )
