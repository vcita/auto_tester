"""API helpers for the payment_setups migration (VCITA2-14008).

Tax creation supporting ``default_for_categories`` (the products/invoice tax helpers
hardcode an empty list), mirroring legacy ``automation-js/api/tax.create_tax``.
"""

from __future__ import annotations

from tests.account_api import account_request

TAXES_PATH = "/business/payments/v1/taxes"


def create_tax(context: dict, name: str, rate: int, default_for_categories: str = "") -> dict:
    """Create a tax (POST business/payments/v1/taxes) and return the created tax object.

    ``default_for_categories`` is a comma-separated string (e.g. "services"); empty means
    the tax is not a category default (matches the legacy ``split(',')`` behavior).
    """
    categories = default_for_categories.split(",") if default_for_categories else []
    response = account_request(
        context,
        "POST",
        TAXES_PATH,
        json={
            "tax": {"name": name, "rate": rate, "default_for_categories": categories},
            "new_api": True,
        },
    )
    tax = response["data"]["tax"]
    tax_uid = tax.get("id") or tax.get("uid")
    if not tax_uid:
        raise AssertionError(f"Tax create returned no id/uid: {tax}")
    tax["id"] = tax_uid
    return tax
