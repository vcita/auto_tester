"""Account-scoped API helpers for the staff_profile subcategory.

Resolves the account owner staff (for scenario 1's initial display-name assertion,
which is dynamic per auto-created account) and creates the second staff for
scenario 2. Thin wrappers over tests.account_api primitives.
"""

from tests.account_api import account_request, create_platform_staff_via_api, pivot_uid


def get_owner_staff(context: dict) -> dict:
    """Return the account owner (first) staff: uid, display_name, email."""
    response = account_request(
        context, "GET", f"/platform/v1/businesses/{pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", []) if isinstance(response, dict) else []
    if not staffs:
        raise ValueError("No staff returned for auto account")
    owner = staffs[0]
    return {
        "uid": owner.get("id") or owner.get("uid"),
        "display_name": owner.get("display_name"),
        "email": owner.get("email"),
    }


def create_user_staff(context: dict, name: str, email: str) -> dict:
    """Create a role=user staff and return uid/name/email."""
    return create_platform_staff_via_api(context, name, email, role="user")
