"""Shared payment-setting mappings for the payment_setups migration (VCITA2-14008).

Single source of truth for the legacy payment_setting semantics used across all four
payment-setups scenarios (automation-js api/service.js `_setPaymentType` +
servicesSettings list parsing).
"""

from __future__ import annotations

# payment_setting -> API charge_type (api/service.js _setPaymentType; "dont display"
# falls through to the free default).
CHARGE_TYPE = {
    "require to pay": "paid_force",
    "suggest to pay": "paid",
    "display a fee": "paid_non_secured",
    "display for a fee": "discuss",
    "display free": "free",
    "dont display": "free",
}


def charge_type_for(payment_setting: str) -> str:
    try:
        return CHARGE_TYPE[payment_setting]
    except KeyError as exc:
        raise ValueError(f"Unknown payment_setting: {payment_setting!r}") from exc


# payment_setting -> services-list payment_type (the assertion column in the feature).
LIST_PAYMENT_TYPE = {
    "require to pay": "required",
    "suggest to pay": "online",
    "display a fee": "online",
    "display for a fee": "for a fee",
    "display free": "free",
    "dont display": "dont display",
}


# price_type -> appointment-dialog fee-type label (createMeetingDialog.selectAppointmentPriceType).
# Appointments collapse the six settings to three fee types; "Fixed price" carries an amount.
APPT_FEE_TYPE = {
    "display free": "No Fee",
    "display for a fee": "Custom price",
    "dont display": "Custom price",
    "require to pay": "Fixed price",
    "suggest to pay": "Fixed price",
    "display a fee": "Fixed price",
}


# payment_setting -> advanced-editor dropdown option label (serviceEditor.js).
EDITOR_OPTION = {
    "require to pay": "Paid - Require to pay at booking",
    "suggest to pay": "Paid - Suggest to pay at booking",
    "display a fee": "Paid - No online payment at booking",
    "display for a fee": 'Price varies - Display as "For a fee"',
    "display free": 'Free - Display as "Free"',
    "dont display": "Free - Don't display a fee",
}
