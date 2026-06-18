"""Setup for the cp_service_link subcategory.

Mirrors the legacy features/tempo/CP/service-link.feature Background: log in to the
isolated account, create a service and a staff member via API such that the service is
provided by BOTH the business owner and the new staff (so the general scheduler link
lands on the staff-select page with two providers).
"""
import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import (
    account_request,
    create_platform_staff_via_api,
    create_service_via_api,
    pivot_uid,
)

SERVICE_NAME = "service"
STAFF_DISPLAY = "staff"
BUSINESS_FALLBACK = "Automation test business"


def _owner_staff(context: dict) -> dict:
    response = account_request(
        context, "GET", f"/platform/v1/businesses/{pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for the auto account owner lookup")
    owner = staffs[0]
    return {
        "uid": owner.get("id") or owner.get("uid"),
        "display_name": owner.get("display_name") or owner.get("full_name"),
    }


def setup_cp_service_link(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
    # Remember the back-office app host (e.g. https://app.meet2know.com); after accessing a
    # live client-portal link the page is on live.meet2know.com, so grabbing the general
    # service link must first return to this host.
    context["sl_app_base"] = page.url.split("/app/")[0]

    print("  Setup Step 2: Resolve owner staff")
    owner = _owner_staff(context)
    context["sl_owner_display"] = owner["display_name"]

    stamp = int(time.time() * 1000)
    staff_email = f"sl_staff_{stamp}@vmeetme.com"
    print("  Setup Step 3: Create staff via API")
    staff = create_platform_staff_via_api(context, STAFF_DISPLAY, staff_email, role="user")
    context["sl_staff_uid"] = staff["uid"]
    context["sl_staff_display"] = staff["name"]
    context["sl_staff_email"] = staff["email"]

    print("  Setup Step 4: Create service via API (provided by owner + staff)")
    service = create_service_via_api(
        context, SERVICE_NAME, staff_uids=[owner["uid"], staff["uid"]]
    )
    context["sl_service_name"] = service["name"]
    context["sl_service_uid"] = service["id"]

    print(
        f"  [OK] cp_service_link setup complete - service '{service['name']}' provided by "
        f"'{owner['display_name']}' + '{staff['name']}' ({staff_email})"
    )
